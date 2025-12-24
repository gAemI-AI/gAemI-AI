#!/bin/bash
# 대시보드 실시간 데이터 흐름 진단 스크립트

set -e

echo "=============================================="
echo "🔍 gAemI 실시간 데이터 진단 시작"
echo "=============================================="
echo ""

# 1. Docker 컨테이너 상태 확인
echo "📦 1단계: Docker 컨테이너 상태 확인"
echo "--------------------------------------"

CONTAINERS=("kafka" "backend" "producer-stock" "elasticsearch")

for container in "${CONTAINERS[@]}"; do
    if docker ps | grep -q "$container"; then
        echo "✅ $container - 실행 중"
    else
        echo "❌ $container - 실행 중지 또는 미존재"
    fi
done
echo ""

# 2. Kafka 토픽 확인
echo "📚 2단계: Kafka 토픽 확인"
echo "--------------------------------------"

if docker ps | grep -q kafka; then
    echo "Kafka 토픽 목록:"
    docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null || echo "❌ Kafka 명령 실패"
    echo ""
else
    echo "⚠️  Kafka 컨테이너가 실행 중이지 않습니다"
    echo ""
fi

# 3. Django 로그에서 WebSocket 관련 메시지 확인
echo "🔌 3단계: Django WebSocket 로그 확인"
echo "--------------------------------------"

if docker ps | grep -q backend; then
    echo "최근 WebSocket 연결 로그:"
    docker logs backend 2>/dev/null | grep -E "Chart WS Connected|WebSocket" | tail -10 || echo "⚠️  연결 로그 미발견"
    echo ""
    
    echo "Kafka Bridge 시작 로그:"
    docker logs backend 2>/dev/null | grep -E "Alert Consumer 시작|Stock Ticks Consumer 시작" | tail -5 || echo "⚠️  시작 로그 미발견"
    echo ""
else
    echo "⚠️  Backend 컨테이너가 실행 중이지 않습니다"
    echo ""
fi

# 4. Producer 데이터 발행 확인
echo "📤 4단계: Producer 데이터 발행 확인"
echo "--------------------------------------"

if docker ps | grep -q producer-stock; then
    echo "최근 Producer 로그:"
    docker logs producer-stock 2>/dev/null | tail -15 || echo "⚠️  로그 미발견"
    echo ""
else
    echo "⚠️  Producer-stock 컨테이너가 실행 중이지 않습니다"
    echo ""
fi

# 5. Elasticsearch 데이터 확인
echo "💾 5단계: Elasticsearch 데이터 확인"
echo "--------------------------------------"

if docker ps | grep -q elasticsearch; then
    echo "Elasticsearch 인덱스 목록:"
    curl -s http://localhost:9200/_cat/indices?v 2>/dev/null | grep -E "raw-stocks|market-indices" || echo "⚠️  주식 데이터 인덱스 미발견"
    echo ""
    
    echo "raw-stocks 인덱스의 최근 데이터 개수:"
    curl -s http://localhost:9200/raw-stocks/_count 2>/dev/null | grep -o '"count":[0-9]*' || echo "⚠️  데이터 조회 실패"
    echo ""
else
    echo "⚠️  Elasticsearch 컨테이너가 실행 중이지 않습니다"
    echo ""
fi

echo "=============================================="
echo "진단 완료"
echo "=============================================="
echo ""
echo "📋 확인 사항:"
echo ""
echo "1️⃣  모든 컨테이너가 실행 중인가?"
echo "2️⃣  Kafka에 'stock-ticks' 토픽이 있는가?"
echo "3️⃣  Django 로그에 'Chart WS Connected' 메시지가 있는가?"
echo "4️⃣  Django 로그에 'Stock Ticks Consumer 시작' 메시지가 있는가?"
echo "5️⃣  Producer가 정기적으로 데이터를 발행하는가?"
echo "6️⃣  Elasticsearch에 'raw-stocks' 인덱스가 있고 데이터가 있는가?"
echo ""
echo "💡 실시간 업데이트 확인 방법:"
echo "   - 브라우저 DevTools (F12) > Console 탭"
echo "   - '[WebSocket ...] 메시지 수신:' 로그 확인"
echo "   - Network > WS 필터로 WebSocket 메시지 확인"
echo ""
