#!/bin/bash
echo "======================================"
echo "   Trading Bot 긴급 수정 스크립트"
echo "======================================"

# 1. .env 파일 생성
echo "1. .env 파일 생성 중..."
cat > .env << 'EOF'
# Discord 설정
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# 서버 설정
PORT=8000

# 웹훅 보안 (선택사항)
WEBHOOK_SECRET=

# KIS 계좌 설정 (나중에 설정)
# KIS1_KEY=
# KIS1_SECRET=
# KIS1_ACCOUNT_NUMBER=
# KIS1_ACCOUNT_CODE=
EOF

echo "✅ .env 파일 생성 완료"

# 2. 템플릿 파일 수정
echo "2. 템플릿 파일 수정 중..."
if [ -f "templates/dashboard.html" ]; then
    # moment() 함수를 now.strftime()으로 변경
    sed -i 's/{{ moment().format('\''YYYY-MM-DD HH:mm:ss'\'') }}/{{ now.strftime('\''%Y-%m-%d %H:%M:%S'\'') }}/g' templates/dashboard.html
    echo "✅ 템플릿 파일 수정 완료"
else
    echo "❌ 템플릿 파일을 찾을 수 없습니다."
fi

# 3. app.py 파일 수정
echo "3. app.py 파일 수정 중..."
if [ -f "app.py" ]; then
    # datetime import 추가 (이미 있으면 중복 추가 안됨)
    if ! grep -q "from datetime import datetime" app.py; then
        sed -i '1i from datetime import datetime' app.py
        echo "✅ datetime import 추가됨"
    fi
    
    # context_processor 추가
    if ! grep -q "inject_now" app.py; then
        # Flask 앱 초기화 후에 추가
        sed -i '/CORS(app)/a\\n@app.context_processor\ndef inject_now():\n    return {'"'"'now'"'"': datetime.now()}' app.py
        echo "✅ context_processor 추가됨"
    fi
    
    echo "✅ app.py 파일 수정 완료"
else
    echo "❌ app.py 파일을 찾을 수 없습니다."
fi

echo ""
echo "======================================"
echo "   수정 완료!"
echo "======================================"
echo ""
echo "다음 명령어로 서버를 재시작하세요:"
echo "pkill -f python"
echo "python app.py"
echo ""
