# data-pjt/flink-jobs/utils/openai_client.py
# 여러개의 텍스트를 한 번에 API로 보내는 로직
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


# GMS 서버
GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

# 클라이언트 초기화 
client = OpenAI(
    api_key=OPENAI_API_KEY,  # .env에 있는 키
    base_url=GMS_BASE_URL    # GMS 주소
)

def get_embeddings_batch(text_list):
    """
    텍스트 리스트를 받아 한 번의 API 호출로 벡터 리스트 반환
    Input: ["기사1 내용", "기사2 내용"]
    Output: [[0.1, ...], [0.2, ...]]
    """
    # 변환할 내용이 없다면 빈 리스트 반환
    if not text_list:
        return []

    try:
        # OpenAI API 호출 
        response = client.embeddings.create(
            input=text_list,
            model=OPENAI_MODEL
        )
        
        # 순서대로 벡터 추출
        embeddings = [data.embedding for data in response.data]
        print(f"[OpenAI] {len(text_list)}건 임베딩 완료")
        return embeddings

    except Exception as e:
        print(f"❌ [OpenAI Error] {e}")
        # 에러 발생 시 빈 리스트 반환 (재시도 로직은 Flink가 담당하도록 함)
        return [[] for _ in text_list] # (참고) 여기서 빈 벡터를 채워서 리턴할 수도 있음