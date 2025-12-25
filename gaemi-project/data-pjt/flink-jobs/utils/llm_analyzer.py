# gaemi-project > data-pjt > flink-jobs > utils > llm_analyzer.py
import json
from openai import OpenAI
from config import OPENAI_API_KEY

# GMS 서버 
GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

# 클라이언트 초기화
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=GMS_BASE_URL
)

def analyze_news_batch(news_items):
    """
    뉴스 리스트를 받아 요약 및 감성 분석 수행 (gpt-4.1-nano)
    
    Args:
        news_items (list): [{'title': '...', 'scraped_text': '...'}, ...]
        
    Returns:
        list: [{'summary': ['...'], 'sentiment': 'POSITIVE'}, ...] (순서 보장)
    """
    if not news_items:
        return []

    results = []
    
    # SYSTEM PROMPT: AI의 페르소나와 출력 형식을 정의
    system_prompt = """
    당신은 주식 투자 전문가입니다. 주어진 뉴스를 분석하여 다음 JSON 형식으로 응답하세요.
    {"summary": ["핵심1", "핵심2", "핵심3"], "sentiment": "POSITIVE" | "NEGATIVE" | "NEUTRAL"}
    
    [Sentiment 기준]
    - POSITIVE: 실적 호조, 계약 체결, 주가 상승 전망, 긍정적 리포트
    - NEGATIVE: 실적 악화, 소송, 규제, 악재, 주가 하락 전망
    - NEUTRAL: 단순 시황, 정보성 기사, 판단 유보
    
    [Summary 기준]
    - 한국어로 3줄 이내 개조식 요약
    - 투자자 관점에서 중요한 정보 위주
    """

    for item in news_items:
        # 본문이 너무 짧으면(스크래핑 실패 등) 제목만 사용
        text_content = item.get('scraped_text', '')
        if len(text_content) < 50:
            text_content = item.get('title', '')

        # 400자 제한 (이미 scraping.py에서 잘려서 오지만 안전장치)
        input_text = f"제목: {item.get('title')}\n내용: {text_content[:400]}"

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano", # 가성비 모델
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text}
                ],
                temperature=0.0, # 일관된 분석을 위해 0 설정
                response_format={"type": "json_object"}, # JSON 강제 모드 (안정성을 위해)
                max_tokens=300
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            # 필드 유효성 검사 (가끔 키가 다르게 올 수 있음 방지)
            summary = parsed_data.get("summary", ["요약 실패"])
            sentiment = parsed_data.get("sentiment", "NEUTRAL")
            
            if isinstance(summary, str): # 리스트가 아니라 문자열로 오면 리스트로 감싸기
                summary = [summary]
                
            results.append({"summary": summary, "sentiment": sentiment})

        except Exception as e:
            print(f"[LLM Analyze Error] {item.get('title')[:10]}... : {e}")
            # 에러 발생 시 기본값 채움 (파이프라인 중단 방지)
            results.append({
                "summary": ["AI 분석을 수행할 수 없습니다."],
                "sentiment": "NEUTRAL"
            })

    print(f"[LLM] {len(news_items)}건 분석 완료")
    return results