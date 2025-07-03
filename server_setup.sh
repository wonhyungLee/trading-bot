#!/bin/bash
echo "======================================"
echo "   Trading Bot - Server Setup"
echo "======================================"

# 1. 홈 디렉토리로 이동
cd ~

# 2. 기존 디렉토리 삭제 (있다면)
if [ -d "trading-bot" ]; then
    echo "기존 trading-bot 디렉토리 삭제 중..."
    rm -rf trading-bot
fi

# 3. GitHub에서 클론 (실제 URL로 변경 필요)
echo "GitHub에서 클론 중..."
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git trading-bot

# 4. 디렉토리 이동
cd trading-bot

# 5. 가상환경 생성
echo "Python 가상환경 생성 중..."
python3 -m venv venv

# 6. 가상환경 활성화
source venv/bin/activate

# 7. 패키지 설치
echo "패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 8. .env 파일 생성
echo "환경 설정 파일 생성 중..."
cp .env.example .env

echo "======================================"
echo "   설치 완료!"
echo "======================================"
echo ""
echo "다음 단계:"
echo "1. nano .env 명령어로 환경 설정 파일 편집"
echo "2. 설정 완료 후 python app.py 실행"
echo ""
echo "현재 위치: $(pwd)"
echo ""
