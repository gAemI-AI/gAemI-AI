# data-pjt/flink-jobs/utils/scraping.py
import requests
from bs4 import BeautifulSoup

def scrape_and_format(link, title):
    """
    url에서 본문을 가져와서 '제목 + 본문 앞부분(400자)' 형태로 반환
    실패 시 제목만 반환
    """
    # User-Agent 헤더: 차단 방지용
    # '맥북을 쓰는 크롬 유저'로 신분증 제출
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    try:
        # 1. 요청 (3초 타임아웃)
        response = requests.get(link, headers=headers, timeout=3)
        response.raise_for_status() # 404, 500 에러 시 즉시 예외 발생 시킴

        # 2. 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. 본문 추출 (일반적인 <p> 태그 수집)
        paragraphs = soup.find_all('p')

        full_text = " ".join([p.get_text() for p in paragraphs])
        
        # 4. 내용이 너무 짧으면 에러 처리
        if len(full_text) < 50:
            raise Exception("Content too short")

        # 5. 앞 400자만 자르기
        summary_text = full_text[:400].strip()
        
        # 6. 최종 포맷: "제목. 본문요약"
        # 제목과 본문을 합쳐서 AI에게 문맥 제공
        final_text = f"{title}. {summary_text}"
        return final_text

    except Exception as e:
        print(f"⚠️ Scraping Failed: {link} -> {e}") # 실패하면 제목만이라도 반환
        return title