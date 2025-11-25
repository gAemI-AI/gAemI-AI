-- Docker가 자동으로 실행하여 테이블 생성
-- DB는 docker-compose에서 생성함

-- 1. stock_master 테이블
CREATE TABLE stock_master (
    stock_id VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market_type VARCHAR(10) NOT NULL
);

-- 데이터 로드 (현재는 테스트용, 추후 수정 필요)
COPY stock_master(stock_id, stock_name, market_type)
FROM '/docker-data/stock_master_for_test.csv'
DELIMITER ','
CSV HEADER;

-- 이외의 데이터 테이블은 Backend에서 주관한다
--  2. users 테이블
-- CREATE TABLE users (
--     user_id BIGSERIAL PRIMARY KEY,
--     username VARCHAR(150) NOT NULL UNIQUE,
--     password VARCHAR(128) NOT NULL,
--     email VARCHAR(254) NOT NULL UNIQUE, -- Django Hashed Password
--     created_at TIMESTAMP NOT NULL DEFAULT NOW()
-- );
-- -- 3. user_watchlist 테이블
-- CREATE TABLE user_watchlist (
--     watchlist_id BIGSERIAL PRIMARY KEY,
--     user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
--     stock_id VARCHAR(10) NOT NULL REFERENCES stock_master(stock_id) ON DELETE CASCADE,
--     created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
--     -- 한 유저가 같은 종목을 중복 추가하는 것을 방지
--     UNIQUE(user_id, stock_id)
-- );

-- -- 4. user_notification_rules 테이블
-- CREATE TABLE user_notification_rules (
--     rule_id BIGSERIAL PRIMARY KEY,
--     user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
--     stock_id VARCHAR(10) NOT NULL REFERENCES stock_master(stock_id) ON DELETE CASCADE,
--     metric_type VARCHAR(20) NOT NULL,
--     operator VARCHAR(10) NOT NULL,
--     target_value VARCHAR(50) NOT NULL,
--     is_active BOOLEAN NOT NULL DEFAULT TRUE
-- );

-- -- 5. triggered_notifications 테이블
-- CREATE TABLE triggered_notifications (
--     notification_id BIGSERIAL PRIMARY KEY,
--     user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
--     stock_name VARCHAR(100) NOT NULL,
--     message TEXT NOT NULL,
--     is_read BOOLEAN NOT NULL DEFAULT FALSE,
--     triggered_at  NOT NULL DEFAULT NOW()
-- );

-- -- 조회 성능을 위한 인덱스 추가
-- CREATE INDEX idx_triggerTIMESTAMPed_at ON triggered_notifications (triggered_at DESC);
-- CREATE INDEX idx_watchlist_user ON user_watchlist (user_id);
-- CREATE INDEX idx_rules_user ON user_notification_rules (user_id);