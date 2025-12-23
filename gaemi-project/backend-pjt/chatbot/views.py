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
                
                content = source.get('scraped_text', '')
                context_text += f"[{date_str}] {source.get('title')}\n내용: {content}\n\n"

            # 시스템 프롬프트 (전문가 페르소나)
            system_prompt = f"""
                당신은 월스트리트 출신의 수석 애널리스트 '개미 AI'입니다.
                사용자의 질문(예: '삼성전자 주가 하락 원인은?')에 대해
                제공된 [최신 뉴스]를 근거로 질문에 직접 답하는 방식으로 설명하세요.

                작성 원칙:
                1. 애널리스트 어조: 보고서체가 아닌 설명체를 사용하세요.
                ("~입니다", "~로 판단됩니다", "~가 핵심입니다")
                2. 질문 중심 답변: 시장 전체 요약보다 질문에서 묻는 대상과 원인을 우선 설명하세요.
                3. 근거 기반: 뉴스에 명시된 사실만 사용하며, 없는 내용은
                "관련 데이터는 기사에 명확히 언급되지 않았습니다"라고 밝혀주세요.
                4. 과도한 포맷 지양: 불필요한 서론·결론 없이 핵심 위주로 작성하세요.

                **답변 고려 사항:**
                질문에 대한 가장 중요한 이유를 분석하세요.
                제공한 최신 뉴스 데이터를 기반으로 원인을 파악하세요.
                투자자 관점에서의 유의할 점이나 조언을 한 문장으로 정리해보세요.

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