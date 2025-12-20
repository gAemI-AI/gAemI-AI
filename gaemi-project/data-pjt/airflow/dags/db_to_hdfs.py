from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
from hdfs import InsecureClient
import os

# 환경변수 로드
PG_HOST = os.getenv("GAEMI_DB_HOST")
PG_DB = os.getenv("GAEMI_DB_NAME")
PG_USER = os.getenv("GAEMI_DB_USER")
PG_PASSWORD = os.getenv("GAEMI_DB_PASSWORD")
HDFS_URL = os.getenv("GAEMI_HDFS_URL")
HDFS_USER = os.getenv("GAEMI_HDFS_USER")

default_args = {
    'owner': 'gaemi',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 20),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# 기간 지난 알람 정보 모으기
def archive_notifications(**kwargs):
    if not PG_HOST:
        raise ValueError("환경변수 로드 실패 docker-compose 확인 필요")

    # 1. 30일 이전 날짜 계산
    target_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    print(f"[Start] {target_date} 이전 알림 데이터 아카이빙 시작")

    conn = psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD)
    
    table_name = "triggered_notifications"
    date_column = "triggered_at"
    
    query = f"SELECT * FROM {table_name} WHERE {date_column} < '{target_date}'"
    
    try:
        df = pd.read_sql(query, conn)

    except Exception as e:
        print(f"조회 실패: {e}")
        conn.close()
        return

    if df.empty: # 테이블이 비어있다면
        print("아카이빙할 데이터가 없습니다.")
        conn.close()
        return

    print(f"📦 조회된 데이터: {len(df)}건")

    # 2. Parquet 변환
    file_name = f"notifications_{target_date}.parquet"
    df.to_parquet(file_name, index=False)

    # 3. HDFS 업로드
    client = InsecureClient(HDFS_URL, user=HDFS_USER)
    hdfs_path = f"/archive/notifications/{datetime.now().year}/{file_name}"
    
    try:
        client.upload(hdfs_path, file_name, overwrite=True)
        print(f"✅ HDFS 업로드 완료: {hdfs_path}")
        
        # 4. DB 삭제 (업로드 성공 시에만 실행)
        cursor = conn.cursor()
        delete_query = f"DELETE FROM {table_name} WHERE {date_column} < '{target_date}'"
        cursor.execute(delete_query)
        conn.commit()
        print(f"🗑️ DB 삭제 완료: {cursor.rowcount}건")
        cursor.close()
        
    except Exception as e:
        print(f"❌ HDFS 업로드 중 에러 발생: {e}")

    # 성공 실패와 상관없이 접속 해제
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
        conn.close()

with DAG(
    'db_archiving_notifications',
    default_args=default_args,
    schedule_interval='0 3 * * *', # 매일 새벽 3시
    catchup=False
) as dag:

    task = PythonOperator(
        task_id='archive_notifications_task',
        python_callable=archive_notifications,
    )