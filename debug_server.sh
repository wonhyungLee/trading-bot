#!/bin/bash
echo "======================================"
echo "   Trading Bot 문제 해결 스크립트"
echo "======================================"

# 1. 현재 실행 중인 프로세스 확인
echo "1. 실행 중인 프로세스 확인:"
ps aux | grep python
echo ""

# 2. 포트 8000 사용 상태 확인
echo "2. 포트 8000 사용 상태:"
sudo netstat -tlnp | grep 8000
echo ""

# 3. 방화벽 상태 확인
echo "3. 방화벽 상태:"
sudo ufw status
echo ""

# 4. 서비스 상태 확인 (시스템 서비스로 등록된 경우)
echo "4. 서비스 상태:"
sudo systemctl status trading-bot 2>/dev/null || echo "서비스가 등록되지 않음"
echo ""

# 5. 로그 파일 확인
echo "5. 로그 파일 확인:"
if [ -f "trading_bot.log" ]; then
    echo "최근 로그 (마지막 20줄):"
    tail -20 trading_bot.log
else
    echo "로그 파일이 없습니다."
fi
echo ""

# 6. .env 파일 존재 확인
echo "6. 환경 설정 파일 확인:"
if [ -f ".env" ]; then
    echo "✅ .env 파일 존재"
    echo "디스코드 웹훅 설정 확인:"
    grep -q "DISCORD_WEBHOOK_URL" .env && echo "✅ DISCORD_WEBHOOK_URL 설정됨" || echo "❌ DISCORD_WEBHOOK_URL 미설정"
else
    echo "❌ .env 파일 없음"
fi
echo ""

# 7. Python 가상환경 확인
echo "7. Python 가상환경 확인:"
if [ -d "venv" ]; then
    echo "✅ 가상환경 존재"
    echo "가상환경 활성화 상태:" 
    echo $VIRTUAL_ENV
else
    echo "❌ 가상환경 없음"
fi
echo ""

# 8. 의존성 설치 확인
echo "8. 주요 패키지 설치 확인:"
source venv/bin/activate 2>/dev/null || echo "가상환경 활성화 실패"
pip list | grep -E "(Flask|ccxt|requests|discord)" || echo "주요 패키지 설치 확인 실패"
echo ""

echo "======================================"
echo "   문제 해결 제안"
echo "======================================"
echo ""
echo "다음 명령어를 순서대로 실행해보세요:"
echo ""
echo "1. 기존 프로세스 종료:"
echo "   pkill -f app.py"
echo ""
echo "2. 가상환경 활성화:"
echo "   source venv/bin/activate"
echo ""
echo "3. 의존성 재설치:"
echo "   pip install -r requirements.txt"
echo ""
echo "4. 직접 실행 (테스트용):"
echo "   python app.py"
echo ""
echo "5. 백그라운드 실행:"
echo "   nohup python app.py > trading_bot.log 2>&1 &"
echo ""
