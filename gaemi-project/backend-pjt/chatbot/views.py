from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from elasticsearch import Elasticsearch
from openai import OpenAI
from datetime import datetime, timedelta

class ChatbotRAGView(APIView):
    permission_classes = [AllowAny] 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.es = Elasticsearch(
            hosts=[{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}]
        )
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    def post(self, request):
        user_question = request.data.get('question')
        if not user_question:
            return Response({"error": "질문을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. 질문 임베딩
            emb_res = self.openai_client.embeddings.create(
                input=user_question,
                model="text-embedding-3-small"
            )
            question_vector = emb_res.data[0].embedding

            # 🌟 [수정 1] 날짜 필터 계산 (밀리초 단위)
            # 현재 시간에서 3일 전 시간을 구한 뒤, 밀리초(x1000)로 변환
            three_days_ago = datetime.now() - timedelta(days=3)
            limit_timestamp = int(three_days_ago.timestamp() * 1000)

            # 2. Elasticsearch 벡터 검색
            search_query = {
                "knn": {
                    "field": "vector",
                    "query_vector": question_vector,
                    "k": 5,
                    "num_candidates": 100,
                    # 🌟 [수정 2] 숫자형 타임스탬프 필터링 (published_at 사용)
                    "filter": {
                        "range": {
                            "published_at": { 
                                "gte": limit_timestamp 
                            }
                        }
                    }
                },
                # 필요한 필드 명시 (published_at 포함)
                "_source": ["title", "scraped_text", "published_at"]
            }

            response = self.es.search(index="news-summary", body=search_query)
            hits = response['hits']['hits']

            if not hits:
                return Response({
                    "answer": "최근 3일 이내에 해당 종목과 관련된 중요 뉴스가 감지되지 않았습니다. \n\n시장이 잠잠하거나, 뉴스 수집 범위를 벗어났을 수 있습니다.",
                    "references": []
                }, status=status.HTTP_200_OK)

            # 3. 프롬프트 구성
            context_text = ""
            for hit in hits:
                source = hit['_source']
                
                # 🌟 [수정 3] 밀리초 타임스탬프를 읽기 좋은 날짜(YYYY-MM-DD)로 변환
                ts = source.get('published_at')
                date_str = "(날짜 없음)"
                if ts:
                    try:
                        # 밀리초(/1000) -> 초 단위 변환 후 datetime 객체 생성
                        dt_obj = datetime.fromtimestamp(ts / 1000)
                        date_str = dt_obj.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                content = source.get('scraped_text', '')[:300] 
                context_text += f"[{date_str}] {source.get('title')}\n내용: {content}\n\n"

            # 시스템 프롬프트 (전문가 페르소나)
            system_prompt = f"""
            당신은 월스트리트 출신의 수석 애널리스트 '개미 AI'입니다.
            사용자의 질문에 대해 제공된 [최신 뉴스]를 바탕으로 전문적이고 통찰력 있는 브리핑을 제공하세요.
            
            **작성 원칙:**
            1. **전문가적 어조:** "~해요" 대신 "~입니다/판단됩니다" 같은 명확하고 신뢰감 있는 어조를 사용하세요.
            2. **구조화된 답변:** 답변을 줄글로 쓰지 말고, 가독성 있게 Markdown 형식으로 소제목을 달아 작성하세요.
            3. **객관성:** 뉴스에 없는 내용은 추측하지 말고 "데이터가 부족합니다"라고 명시하세요.
            
            **답변 형식(Template):**
            ### 📊 시장 핵심 요약
            (전반적인 뉴스 분위기를 1-2문장으로 요약)
            
            ### 💡 주요 이슈 분석
            - **(이슈 키워드):** (상세 내용 설명)
            - **(이슈 키워드):** (상세 내용 설명)
            
            ### 🚀 투자 관점 (Insight)
            (제공된 뉴스가 호재인지 악재인지, 투자자가 유의해야 할 점을 한 줄로 조언)
            
            ---
            [최신 뉴스 데이터]
            {context_text}
            """

            # 4. GPT 답변 생성 (GMS 모델 사용)
            chat_res = self.openai_client.chat.completions.create(
                model="gpt-4.1-nano", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.3
            )
            
            answer = chat_res.choices[0].message.content

            return Response({
                "answer": answer,
                "references": [h['_source'].get('title') for h in hits]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ RAG Error: {e}")
            return Response(
                {"answer": "일시적인 시스템 오류로 분석 리포트를 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.", "references": []}, 
                status=status.HTTP_200_OK
            )