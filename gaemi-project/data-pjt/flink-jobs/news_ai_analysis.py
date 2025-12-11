# data-pjt/flink-jobs/news_ai_analysis.py
# 메인 Flink Job: Window 함수 활용 배치처리

import json
import logging
import sys  
import os  

# 현재 파일의 위치를 시스템 경로에 추가 (Flink가 utils를 찾을 수 있게)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time
from pyflink.datastream.functions import ProcessWindowFunction, MapFunction, FilterFunction
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy

# 커스텀 모듈
from config import *
from utils.scraping import scrape_and_format
from utils.openai_client import get_embeddings_batch
from utils.es_connector import save_news_to_es

# -----------------------------------------------------------------------
#  중복 제거 필터 
# -----------------------------------------------------------------------
class DeduplicateFunction(FilterFunction):
    def __init__(self):
        self.seen_ids = set() # 메모리에 ID 저장

    def filter(self, value):
        try:
            data = json.loads(value) # JSON으로 불러오기
            news_id = data.get('news_id') # news_id 추출
            
            if news_id in self.seen_ids: # 중복된 news_id라면
                print(f"[Duplicate Skip]: {news_id}")
                return False # 버림
            
            # 새로운 ID면 저장하고 통과
            self.seen_ids.add(news_id)
            
            # 메모리 무한 증가 방지: 10,000개 넘으면 초기화 or 오래된 것 삭제
            if len(self.seen_ids) > 10000:
                self.seen_ids.clear()
            return True
        
        except:
            return False # 파싱 에러나면 그냥 버림 (안정성 확보)

# -----------------------------------------------------------------------
# Window가 닫힐 때(5초마다) 실행되는 배치 함수
# -----------------------------------------------------------------------
class BatchEmbeddingWindow(ProcessWindowFunction):
    def process(self, key, context, elements):
        """
        elements: 5초 동안 쌓인 뉴스 데이터들의 리스트 (Iterator)
        """
        news_list = [e for e in elements]
        
        # 데이터가 없다면 바로 return
        if not news_list:
            return

        print(f"[Batch Window] {len(news_list)}개 뉴스 처리 시작")

        # 1. 임베딩할 텍스트 추출 ('scraped_text' 필드) -> 리스트로 변환
        texts_to_embed = [item['scraped_text'] for item in news_list]

        # 2. 텍스트만 뽑아 한 번에 OpenAI API 호출
        vectors = get_embeddings_batch(texts_to_embed)

        # 3. 결과 매핑 (기존 데이터에 벡터 추가)
        for i, news_item in enumerate(news_list):
            if i < len(vectors) and vectors[i]: # 인덱스 범위 내 + vector 결과값이 있는 경우
                news_item['vector'] = vectors[i] # 벡터 필드 추가
                news_item['scraped_text'] = texts_to_embed[i] # 본문 내용 저장 (데이터 디버깅을 위해 살려둠 -> 삭제 가능)
    
            else:
                news_item['vector'] = [] # 실패 시 빈 리스트

            # 다음 단계(Sink)로 내보냄
            yield news_item

# -----------------------------------------------------------------------
# 메인 파이프라인
# -----------------------------------------------------------------------
def run():
    """
    kafka에서 원신 뉴스(JSON)읽기 -> 레코드에 대해 웹스크래핑해서 scraped_text 채움 
    -> 일정 시간 배치 윈도우로 모아 임베딩 생성 -> 임베딩이 붙은 레코드를 ES에 저장 -> 잡 실행
    """
    env = StreamExecutionEnvironment.get_execution_environment() # flink 실행 환경 가져오기
    env.set_parallelism(1) # 병렬도 1(단일 파티션에서 실행됨, 병렬 처리 없음)
    # 현재는 일꾼을 1명만 사용 -> 뉴스가 폭발적으로 많아지면 처리 속도가 데이터 유입 속도를 따라가지 못해 Lag 걸릴 수도 있음
    # 따라서, 배포를 위해서는 비동기 처리(Async I/O)를 고려해야 함

    # 안정성 추가: 체크포인트 활성화 (1분마다 저장)
    # Job이 죽었다 살아나도 마지막으로 읽은 Kafka 위치부터 다시 시작함
    env.enable_checkpointing(60000)

    # 현재 파일의 위치를 기준으로 경로 잡기
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # utils 폴더를 통째로 일꾼들에게 배포
    env.add_python_file(os.path.join(current_dir, "utils"))
    
    # config.py 파일도 배포
    env.add_python_file(os.path.join(current_dir, "config.py"))

    # 1. Kafka Source 연결
    source = KafkaSource.builder() \
        .set_bootstrap_servers(KAFKA_BROKER) \
        .set_topics(TOPIC_NEWS_RAW) \
        .set_group_id(GROUP_ID) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    stream = env.from_source(source, WatermarkStrategy.no_watermarks(), "NewsKafkaSource")

    # JSON 파싱 전에 ID만 보고 중복 처리
    deduped_stream = stream.filter(DeduplicateFunction())

    # 3. JSON 파싱 & 스크래핑 (Map)
    # 윈도우로 묶기 전에 스크래핑을 먼저 해야 임베딩할 텍스트가 생김
    def scrape_mapper(raw_json):
        try:
            data = json.loads(raw_json) # json 불러오기
            full_text = scrape_and_format(data['link'], data['title'])
            data['scraped_text'] = full_text # 임시 필드에 저장
            return data
        
        except Exception as e:
            print(f"Parsing Error: {e}")
            return None

    # None 필터링
    scraped_stream = stream.map(scrape_mapper).filter(lambda x: x is not None)

    # 4. 배치 처리 (Window + Embedding)
    # key_by(lambda x: 1) -> 모든 뉴스를 하나의 창구로 모음 (Global Window 효과)
    # 윈도우 연산이 키당 하나의 파티션에서 실행되므로 BatchEmbeddingWindow가 단일 스레드로 배치 처리
    # -> 여러 레코드를 모아 batch로 OpenAI 임베딩 호출하려는 목적
    embedded_stream = scraped_stream \
        .key_by(lambda x: 1) \
        .window(TumblingProcessingTimeWindows.of(Time.seconds(BATCH_WINDOW_SECONDS))) \
        .process(BatchEmbeddingWindow()) # 5초 뒤에 모인 데이터를 한 번에 처리

    # 5. Elasticsearch 저장 (Sink)
    embedded_stream.map(save_news_to_es)

    print("News AI Analysis Job Started...")
    env.execute("News AI Analysis Job")

if __name__ == "__main__":
    run()