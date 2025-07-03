#!/bin/bash
echo "======================================"
echo "   웹훅 서버 진단 스크립트"
echo "======================================"

# 서버 IP 확인
SERVER_IP=$(curl -s ifconfig.me)
echo "서버 IP: $SERVER_IP"
echo ""

# 1. 기본 웹 페이지 테스트
echo "1. 기본 웹 페이지 테스트:"
HTTP_RESPONSE=$(curl -s -w "%{http_code}" http://localhost/)
echo "로컬 응답: $HTTP_RESPONSE"

EXTERNAL_RESPONSE=$(curl -s -w "%{http_code}" http://$SERVER_IP/ --connect-timeout 10)
echo "외부 응답: $EXTERNAL_RESPONSE"
echo ""

# 2. Nginx 상태 확인
echo "2. Nginx 상태:"
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 실행 중"
else
    echo "❌ Nginx 정지됨"
fi
echo ""

# 3. Python 앱 상태 확인
echo "3. Python 앱 상태:"
if pgrep -f "python.*app.py" > /dev/null; then
    echo "✅ Python 앱 실행 중"
    echo "프로세스 ID: $(pgrep -f "python.*app.py")"
else
    echo "❌ Python 앱 정지됨"
fi
echo ""

# 4. 포트 8000 테스트 (Python 앱 직접)
echo "4. Python 앱 직접 테스트 (포트 8000):"
PYTHON_RESPONSE=$(curl -s -w "%{http_code}" http://localhost:8000/ --connect-timeout 5)
echo "포트 8000 응답: $PYTHON_RESPONSE"
echo ""

# 5. 웹훅 엔드포인트 테스트
echo "5. 웹훅 엔드포인트 테스트:"
echo "=== 포트 80 (Nginx를 통해) ==="
WEBHOOK_80=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST http://localhost/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}' --connect-timeout 5)
echo "응답: $WEBHOOK_80"

echo ""
echo "=== 포트 8000 (Python 앱 직접) ==="
WEBHOOK_8000=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST http://localhost:8000/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}' --connect-timeout 5)
echo "응답: $WEBHOOK_8000"
echo ""

# 6. 외부에서 웹훅 테스트
echo "6. 외부에서 웹훅 테스트:"
EXTERNAL_WEBHOOK=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST http://$SERVER_IP/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{"test": "external"}' --connect-timeout 10)
echo "외부 웹훅 응답: $EXTERNAL_WEBHOOK"
echo ""

# 7. 로그 파일 확인
echo "7. 최근 로그 확인:"
if [ -f "trading_bot.log" ]; then
    echo "=== 최근 5줄 ==="
    tail -5 trading_bot.log
else
    echo "❌ 로그 파일 없음"
fi
echo ""

# 8. Nginx 설정 확인
echo "8. Nginx 설정 확인:"
if [ -f "/etc/nginx/sites-enabled/trading-bot" ]; then
    echo "✅ Nginx 설정 파일 존재"
else
    echo "❌ Nginx 설정 파일 없음"
fi

# Nginx 설정 테스트
sudo nginx -t 2>&1 | head -3
echo ""

echo "======================================"
echo "   권장 조치"
echo "======================================"
echo ""
if [[ "$PYTHON_RESPONSE" == *"200"* ]]; then
    echo "✅ Python 앱이 정상 작동 중"
else
    echo "❌ Python 앱 문제 - 재시작 필요"
    echo "   python app.py"
fi

if [[ "$HTTP_RESPONSE" == *"200"* ]]; then
    echo "✅ Nginx 프록시 정상 작동"
else
    echo "❌ Nginx 설정 문제 - 설정 확인 필요"
fi

if [[ "$EXTERNAL_RESPONSE" == *"200"* ]]; then
    echo "✅ 외부 접근 가능"
else
    echo "❌ 외부 접근 불가 - 방화벽/보안그룹 확인 필요"
fi
echo ""
