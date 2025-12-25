# data-pjt/flink-jobs/utils/db_connector.py
# Flink Job이 PostgreSQL DB에 접속해서 데이터를 쓰거나 읽는 모듈 모음
# - (안정성) DB 연결 실패시 재시도 로직 포함
# - (편의성) 데이터 조회 결과 JSON 변환
# - (데이터 무결성) 트랜잭션 관리(commit/rollback) 확실하게 처리

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import time
import sys

from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

# DB 연결 및 객체 반환 함수
def get_db_connection(max_retries=3, retry_delay=2):
    """
    PostgreSQL 연결 객체 반환 
    - 디폴트 3번까지 재시도
    """
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            return conn
        
        except Exception as e:
            print(f"⚠️ [DB Connect Fail] {e} (시도 {attempt + 1}/{max_retries})")
            sys.stdout.flush() # 로그 즉시 출력
            
            # 마지막 시도가 아니면 잠시 기다렸다 다시 시도
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print("❌ [DB] 연결 실패")
    sys.stdout.flush()
    return None


# 알림 규칙 로딩 함수
def load_active_rules():
    """
    DB에서 활성화된 알림 규칙 모두 조회
    NotificationProcessor가 시작될 때 + 주기적으로 호출
    """
    conn = get_db_connection()
    # 연결 객체 없으면 빈 리스트 반환
    if not conn: return []
    
    try:
        # cursor_factory=RealDictCursor: 결과를 딕셔너리로 받기 (JSON)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT 
                    nr.rule_id, nr.user_id, nr.target_value, nr.operator, nr.metric_type,
                    sm.stock_id, sm.stock_name
                FROM user_notification_rules nr
                JOIN stock_master sm ON nr.stock_id = sm.stock_id
                WHERE nr.is_active = TRUE
            """
            cursor.execute(query)
            rules = cursor.fetchall() # 모든 결과 가져오기
            
            print(f"[DB] 활성 규칙 {len(rules)}개 로딩 완료")
            sys.stdout.flush()
            return [dict(rule) for rule in rules]
            
    except Exception as e:
        print(f"❌ [DB Load Rules Error] {e}")
        sys.stdout.flush()
        return []
    
    # 실패 성공과 상관없이 DB 연결 해제
    finally:
        if conn: conn.close()

# 알림 결과 저장 함수
def save_triggered_notification(user_id, rule_id, stock_name, message):
    """
    조건이 만족되어 알람이 발생한 경우 그 내역을 DB에 저장
    - 저장이 되어야 프론트엔드 알림함에 뜸
    """
    conn = get_db_connection()

    if not conn: return None
    
    try:
        with conn.cursor() as cursor:
            # INSERT 쿼리: 알림 내역 테이블에 데이터 추가
            # rule_id를 메시지에 포함시켜서 중복 체크 시 참조 가능하게 함
            query = """
                INSERT INTO triggered_notifications 
                (user_id, stock_name, message, is_read, triggered_at)
                VALUES (%s, %s, %s, FALSE, NOW())
                RETURNING notification_id
            """
            # 메시지에 rule_id를 마크처럼 붙임 (check_recent_alert에서 검색할 때 사용)
            message_with_id = f"{message} [규칙#{rule_id}]"
            cursor.execute(query, (user_id, stock_name, message_with_id))

            # 방금 생성된 ID 받아오기
            notification_id = cursor.fetchone()[0]
            conn.commit() # 커밋으로 DB 저장
            
            print(f"[DB] 알림 저장 완료 - ID: {notification_id}")
            sys.stdout.flush()
            return notification_id 
            
    except Exception as e:
        print(f"❌ [DB Save Notification Error] {e}")
        sys.stdout.flush()
        conn.rollback() # 에러나면 작업 취소 (되돌리기)
        return None
    
    # 성공 실패와 상관없이 연결 해제
    finally:
        if conn: conn.close()


# 중복 알림 방지
def check_recent_alert(rule_id, cooldown_seconds=300):
    """
    해당 규칙(rule_id)으로 최근 5분(300초) 내에 알람을 보낸 이력이 있는지 확인
    - 주가가 왔다갔다 할때 알림 폭탄을 막기 위해 
    """
    conn = get_db_connection()
    if not conn: return False # DB 연결 안 되면 일단 알림 보내도록 False 반환
    
    try:
        with conn.cursor() as cursor:
            # 1. 시간 계산: 현재 시간에서 5분을 뺀 시간을 구함
            # SQL 문법(INTERVAL) 에러를 피하기 위해 파이썬에서 계산해서 넘김
            limit_time = datetime.now() - timedelta(seconds=cooldown_seconds)
            
            # 2. 조회 쿼리:
            # 메시지 내용에 식별자가 포함되어 있고,
            # 발생 시간이 limit_time보다 최신인 데이터가 몇 개인지 셈
            query = """
                SELECT COUNT(*) 
                FROM triggered_notifications
                WHERE message LIKE %s
                  AND triggered_at > %s
            """
            cursor.execute(query, (f'%규칙#{rule_id}%', limit_time))
            count = cursor.fetchone()[0]
            
            # 개수가 0보다 크면 = 최근에 보낸 적이 있다 (True)
            return count > 0
            
    except Exception as e:
        print(f"⚠️ [DB Cooldown Check Error] {e}")
        sys.stdout.flush()
        return False
    # 성공 실패와 상관없이 연결 해제
    finally:
        if conn: conn.close()