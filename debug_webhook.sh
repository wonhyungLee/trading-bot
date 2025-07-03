#!/bin/bash
echo "======================================"
echo "   웹훅 디버깅 스크립트"
echo "======================================"

# 1. 현재 서버 상태 확인
echo "1. 서버 프로세스 확인:"
ps aux | grep python
echo ""

# 2. 포트 80 사용 확인
echo "2. 포트 80 상태 확인:"
sudo netstat -tlnp | grep :80
echo ""

# 3. Nginx 상태 확인
echo "3. Nginx 상태 확인:"
sudo systemctl status nginx --no-pager
echo ""

# 4. .env 파일 확인
echo "4. 환경 설정 확인:"
if [ -f ".env" ]; then
    echo "✅ .env 파일 존재"
    echo "디스코드 웹훅 설정:"
    grep DISCORD .env || echo "❌ DISCORD_WEBHOOK_URL 설정 안됨"
else
    echo "❌ .env 파일 없음"
fi
echo ""

# 5. 로그 파일 확인
echo "5. 최근 로그 확인:"
if [ -f "trading_bot.log" ]; then
    echo "마지막 10줄:"
    tail -10 trading_bot.log
else
    echo "로그 파일 없음"
fi
echo ""

# 6. 웹훅 엔드포인트 테스트
echo "6. 로컬 웹훅 테스트:"
RESPONSE=$(curl -s -w "%{http_code}" -X POST http://localhost/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TEST",
    "action": "buy", 
    "quantity": 1,
    "account": "kis1"
  }')

echo "응답 코드: $RESPONSE"
echo ""

# 7. 외부에서 접근 테스트
echo "7. 외부 접근 테스트:"
SERVER_IP=$(curl -s ifconfig.me)
echo "서버 IP: $SERVER_IP"

EXTERNAL_RESPONSE=$(curl -s -w "%{http_code}" -X POST http://$SERVER_IP/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "EXTERNAL_TEST",
    "action": "buy", 
    "quantity": 1,
    "account": "kis1"
  }')

echo "외부 응답 코드: $EXTERNAL_RESPONSE"
echo ""

echo "======================================"
echo "   권장 조치 사항"
echo "======================================"
echo ""
echo "1. 로그에서 'Received TradingView webhook' 메시지 확인"
echo "2. 디스코드 웹훅 URL이 올바른지 확인"
echo "3. 오라클 클라우드 보안 그룹에서 포트 80 개방 확인"
echo "4. 트레이딩뷰 알람 설정에서 웹훅 URL 확인"
echo ""
