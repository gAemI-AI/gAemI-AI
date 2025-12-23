# gaemi-project > data-pjt > airflow > dags > es_to_hdfs.py
# stock data, news data를 처리
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers
import pandas as pd
from hdfs import InsecureClient
import os

# 환경변수 로드
ES_HOST = os.getenv("GAEMI_ES_HOST")
HDFS_URL = os.getenv("GAEMI_HDFS_URL")
HDFS_USER = os.getenv("GAEMI_HDFS_USER")

default_args = {
    'owner': 'gaemi',
    'start_date': datetime(2025, 12, 20),
    'retries': 3,
}

# es에서 특정 기간에 해당하는 데이터 아카이빙
# 함수를 정의해서 index, days_to_keep을 설정하여 재활용할 수 있도록 정의
def archive_es_index(index_name, days_to_keep, date_field='timestamp', is_epoch_ms=False, **kwargs):
    
    if not ES_HOST:
        raise ValueError("환경변수 로드 실패 docker-compose 파일 확인 필요")

    es = Elasticsearch([ES_HOST])
    
    # 날짜 계산
    limit_dt = datetime.now() - timedelta(days=days_to_keep)
    
    # 쿼리 조건 생성
    if is_epoch_ms:
        # Producer가 int(timestamp * 1000)으로 보냈으므로 쿼리도 숫자로 해야 함
        target_value = int(limit_dt.timestamp() * 1000)
        print(f"[Start] {index_name} 아카이빙 (기준: {target_value} 미만)")
    else:
        # 일반 날짜 필드 (ISO8601 문자열)
        target_value = limit_dt.strftime('%Y-%m-%dT%H:%M:%S')
        print(f"[Start] {index_name} 아카이빙 (기준: {target_value} 미만)")

    # Scroll Query
    query = {
        "query": {
            "range": {
                date_field: {"lt": target_value}
            }
        }
    }
    
    try:
        scan_docs = helpers.scan(es, query=query, index=index_name, scroll='2m')
        data = [doc['_source'] for doc in scan_docs]
    except Exception as e:
        print(f"인덱스 조회 실패 ({index_name}): {e}")
        return

    if not data:
        print(f"{index_name}: 이동할 데이터가 없습니다.")
        return

    print(f"📦 조회된 데이터: {len(data)}건")
    
    # Parquet 저장 및 업로드
    df = pd.DataFrame(data)
    file_name = f"{index_name}_{datetime.now().strftime('%Y%m%d')}.parquet"
    df.to_parquet(file_name, index=False)

    client = InsecureClient(HDFS_URL, user=HDFS_USER)
    hdfs_path = f"/archive/{index_name}/{datetime.now().year}/{file_name}"
    
    try:
        client.upload(hdfs_path, file_name, overwrite=True)
        print(f"✅ HDFS 업로드 완료: {hdfs_path}")

        # ES 삭제
        es.delete_by_query(index=index_name, body=query)
        print(f"🗑️ ES 데이터 삭제 완료")
    except Exception as e:
        print(f"❌ 처리 중 에러 발생: {e}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

with DAG(
    'es_archiving_pipeline',
    default_args=default_args,
    schedule_interval='30 3 * * *',
    catchup=False
) as dag:

    # Task 1: 뉴스 아카이빙 (90일 보관) -> 리포트 등을 위해 3달까지는 우선 보관
    # timestamp 필드가 Epoch MS(숫자)임 -> is_epoch_ms=True 설정 필수
    archive_news = PythonOperator(
        task_id='archive_news',
        python_callable=archive_es_index,
        op_kwargs={
            'index_name': 'news-summary', 
            'days_to_keep': 90, 
            'date_field': 'published_at',
            'is_epoch_ms': True 

        },
    )

    # Task 2: 주가 틱 아카이빙 (14일 보관)
    # timestamp 필드가 Epoch MS(숫자)임 -> is_epoch_ms=True 설정 필수
    archive_stocks = PythonOperator(
        task_id='archive_stocks',
        python_callable=archive_es_index,
        op_kwargs={
            'index_name': 'raw-stocks', 
            'days_to_keep': 14, 
            'date_field': 'timestamp', 
            'is_epoch_ms': True 
        },
    )

    archive_news >> archive_stocks # 순서 정의해주기