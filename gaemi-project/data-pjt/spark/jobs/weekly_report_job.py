import sys
import os
import json
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, lit, max as spark_max, min as spark_min, 
    first, last, collect_list, when, array_join, udf, row_number
)
from pyspark.sql.window import Window
from pyspark.sql.types import StringType

# OpenAI 라이브러리
import openai

# -------------------------------------------------------------------------
# 1. 환경변수 로드 (.env 파일)
# -------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

try:
    PG_HOST = os.environ.get("PG_HOST", "db")
    PG_DB = os.environ.get("PG_DB", "gaemi_ai")
    PG_USER = os.environ.get("PG_USER", "gaemi")
    PG_PASS = os.environ.get("PG_PASS", "gaemigaemi11")
    ES_HOST = os.environ.get("ES_HOST", "elasticsearch")
    ES_PORT = os.environ.get("ES_PORT", "9200")
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError as e:
    print(f"❌ [Error] 환경변수 {e}가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    sys.exit(1)

# GMS 주소 설정
GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

# -------------------------------------------------------------------------
# 2. Spark Session 생성
# -------------------------------------------------------------------------
def get_spark_session():
    return SparkSession.builder \
        .appName("WeeklyReportJob") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.7.2.jar,/opt/spark/jars/elasticsearch-spark-30_2.12-8.11.1.jar") \
        .config("spark.es.nodes", ES_HOST) \
        .config("spark.es.port", ES_PORT) \
        .config("spark.es.nodes.wan.only", "true") \
        .getOrCreate()

# -------------------------------------------------------------------------
# 3. 데이터 로드 함수들
# -------------------------------------------------------------------------
def get_target_stocks(spark):
    """
    PostgreSQL의 Watchlist와 StockMaster를 조인하여 대상 종목 추출
    """
    jdbc_url = f"jdbc:postgresql://{PG_HOST}:5432/{PG_DB}"
    properties = {"user": PG_USER, "password": PG_PASS, "driver": "org.postgresql.Driver"}

    try:
        watchlist_df = spark.read.jdbc(jdbc_url, "user_watchlist", properties=properties)
        stock_master_df = spark.read.jdbc(jdbc_url, "stock_master", properties=properties)

        target_df = watchlist_df.join(stock_master_df, "stock_id") \
            .select(col("stock_id"), col("stock_name")).distinct()
        
        count = target_df.count()
        print(f"🎯 리포트 생성 대상 종목 수: {count}")
        return target_df
    except Exception as e:
        print(f"❌ [DB Error] PostgreSQL 연결 실패: {e}")
        return None

def get_weekly_prices(spark, start_dt, end_dt):
    """
    Elasticsearch 'raw-stocks'에서 주간 데이터 집계
    (timestamp = epoch millis 기준, OS 무관)
    """

    # ✅ 뉴스 ES와 완전히 동일한 시간 변환 패턴
    start_ts = int(datetime.combine(start_dt, datetime.min.time()).timestamp() * 1000)
    end_ts = int(datetime.combine(end_dt, datetime.max.time()).timestamp() * 1000)

    es_query = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": start_ts,
                    "lte": end_ts
                }
            }
        }
    }

    try:
        raw_df = (
            spark.read.format("org.elasticsearch.spark.sql")
            .option("es.resource", "raw-stocks")
            .option("es.query", json.dumps(es_query))
            # 🔒 안전장치 (타입 꼬임 방지)
            .option(
                "es.read.field.include",
                "stock_code,current_price,high_price,low_price,timestamp"
            )
            .load()
        )

        if raw_df.rdd.isEmpty():
            print("⚠️ [ES] 해당 기간의 주가 데이터가 없습니다.")
            return None

        window_first = Window.partitionBy("stock_code").orderBy("timestamp")
        window_last = Window.partitionBy("stock_code").orderBy(col("timestamp").desc())
        window_agg = Window.partitionBy("stock_code")

        price_stats = raw_df.select(
            col("stock_code"),
            first("current_price").over(window_first).alias("start_price"),
            first("current_price").over(window_last).alias("end_price"),
            spark_min("low_price").over(window_agg).alias("weekly_low"),
            spark_max("high_price").over(window_agg).alias("weekly_high")
        ).distinct()

        return price_stats.withColumn(
            "weekly_return",
            ((col("end_price") - col("start_price")) / col("start_price")) * 100
        )

    except Exception as e:
        print(f"❌ [ES Error] 주가 데이터 조회 실패: {e}")
        return None
    
def get_weekly_news(spark, target_stocks_df, start_dt, end_dt):
    """
    Elasticsearch 'news-summary'에서 뉴스 가져오기
    """
    
    # 날짜(String)를 Unix Timestamp(Long, ms 단위)로 변환
    start_ts = int(datetime.combine(start_dt, datetime.min.time()).timestamp() * 1000)
    end_ts = int(datetime.combine(end_dt, datetime.max.time()).timestamp() * 1000)

    es_query = {
        "query": {
            "range": {
                "published_at": { 
                    "gte": start_ts,
                    "lte": end_ts
                }
            }
        }
    }
    
    try:
        # ✅ [수정 핵심] 'summary' 필드를 강제로 배열(Array)로 읽으라고 지정
        news_df = spark.read.format("org.elasticsearch.spark.sql") \
            .option("es.resource", "news-summary") \
            .option("es.query", json.dumps(es_query)) \
            .option("es.read.field.as.array.include", "summary") \
            .load()
        
        # 이제 summary는 Array<String> 타입이므로 array_join 사용 가능
        news_flat = news_df.withColumn("summary_text", array_join(col("summary"), " ")) \
                           .select("title", "summary_text")

        from pyspark.sql.functions import broadcast

        matched_news = news_flat.join(
            broadcast(target_stocks_df), 
            news_flat.title.contains(target_stocks_df.stock_name) | news_flat.summary_text.contains(target_stocks_df.stock_name)
        )

        grouped_news = matched_news.groupBy("stock_id") \
            .agg(collect_list("title").alias("news_titles"))
        
        return grouped_news
    except Exception as e:
        print(f"⚠️ [ES Warning] 뉴스 데이터 조회 실패 ('news-summary' 인덱스 확인 필요): {e}")
        return None

# -------------------------------------------------------------------------
# 4. OpenAI 리포트 생성 UDF
# -------------------------------------------------------------------------
def generate_ai_report(stock_name, return_rate, news_titles):
    if not news_titles:
        news_context = "관련된 주요 뉴스가 없습니다."
    else:
        news_context = "\n".join([f"- {t}" for t in news_titles[:5]])

    prompt = f"""
    [주식 주간 리포트 작성]
    종목명: {stock_name}
    주간 수익률: {return_rate:.2f}%
    관련 뉴스:
    {news_context}

    위 데이터를 바탕으로 투자자에게 보낼 주간 리포트를 작성해줘. 
    말투는 '해요체'로 친절하게 작성해. 
    수익률에 따라 긍정/부정 톤을 유지해.

    작성 원칙:
            1. 전문가적 어조: "~해요" 대신 "~입니다/판단됩니다" 같은 명확하고 신뢰감 있는 어조를 사용하세요.
            2. 구조화된 답변: 답변을 줄글로 쓰지 말고, 가독성 있게 Markdown 형식으로 소제목을 달아 작성하세요.
            3. 객관성: 근거가 없는 내용은 추측하지 말고 사실 기반으로 내용을 구성하세요.
    """
    
    try:
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=GMS_BASE_URL
        )
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "너는 전문 주식 애널리스트야."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI 분석 실패: {str(e)}"

ai_report_udf = udf(generate_ai_report, StringType())

# -------------------------------------------------------------------------
# 5. PostgreSQL 저장 (JDBC Upsert)
# -------------------------------------------------------------------------
def save_to_postgres(partition):
    conn = None
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASS
        )
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO weekly_reports 
        (stock_id, start_date, end_date, weekly_return, weekly_high, weekly_low, start_price, end_price, summary_text, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (stock_id, start_date) 
        DO UPDATE SET 
            weekly_return = EXCLUDED.weekly_return,
            end_price = EXCLUDED.end_price,
            summary_text = EXCLUDED.summary_text,
            created_at = NOW();
        """
        
        for row in partition:
            cursor.execute(sql, (
                row.stock_id,
                row.start_date,
                row.end_date,
                float(row.weekly_return),
                int(row.weekly_high),
                int(row.weekly_low),
                int(row.start_price),
                int(row.end_price),
                row.summary_text
            ))
        
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"❌ [DB Error] 저장 실패: {e}")
    finally:
        if conn: conn.close()

# -------------------------------------------------------------------------
# 6. 메인 실행 블록
# -------------------------------------------------------------------------
if __name__ == "__main__":
    spark = get_spark_session()
    
    today = datetime.now().date()
    end_date = today
    start_date = today - timedelta(days=7) 
    
    print(f"📅 리포트 대상 기간: {start_date} ~ {end_date}")

    targets = get_target_stocks(spark)
    
    if targets and targets.count() > 0:
        prices = get_weekly_prices(spark, start_date, end_date)
        news = get_weekly_news(spark, targets, start_date, end_date)
        
        if prices:
            final_df = targets.join(prices, targets.stock_id == prices.stock_code, "inner")
            
            if news:
                final_df = final_df.join(news, "stock_id", "left")
            else:
                final_df = final_df.withColumn("news_titles", lit(None).cast("array<string>"))

            final_df = final_df.select(
                targets.stock_id,
                targets.stock_name,
                prices.weekly_return,
                prices.weekly_high,
                prices.weekly_low,
                prices.start_price,
                prices.end_price,
                col("news_titles")
            )

            print("🤖 AI 리포트 생성 중... (시간이 좀 걸릴 수 있습니다)")
            report_df = final_df.withColumn(
                "summary_text", 
                ai_report_udf(col("stock_name"), col("weekly_return"), col("news_titles"))
            ).withColumn("start_date", lit(start_date)) \
             .withColumn("end_date", lit(end_date))

            print("💾 데이터베이스 저장 중...")
            report_df.foreachPartition(save_to_postgres)
            print("✅ 주간 리포트 생성 및 저장 완료!")
        else:
            print("⚠️ 주가 데이터가 없어 리포트를 생성하지 못했습니다.")
    else:
        print("⚠️ 리포트 생성 대상 종목(Watchlist)이 없습니다.")

    spark.stop()