@echo off
echo ====================================
echo    Trading Bot - GitHub Upload
echo ====================================

REM Git 초기화
git init

REM .gitignore 파일 확인
if not exist .gitignore (
    echo .gitignore 파일이 없습니다. 생성 중...
    echo .env > .gitignore
    echo __pycache__/ >> .gitignore
    echo *.pyc >> .gitignore
    echo *.log >> .gitignore
    echo .DS_Store >> .gitignore
    echo node_modules/ >> .gitignore
    echo venv/ >> .gitignore
    echo .vscode/ >> .gitignore
)

REM 파일 추가
git add .

REM 커밋
git commit -m "Initial commit: Trading Bot v1.0"

REM GitHub 원격 저장소 연결 (여기서 YOUR_USERNAME과 YOUR_REPO를 실제 값으로 변경)
echo.
echo 주의: 아래 명령어에서 YOUR_USERNAME과 YOUR_REPO를 실제 값으로 변경하세요
echo git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo.
pause

REM 실제 명령어 실행은 수동으로 하세요
echo 다음 명령어를 순서대로 실행하세요:
echo 1. git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo 2. git push -u origin main
echo.
pause
