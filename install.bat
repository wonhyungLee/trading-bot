@echo off
REM Trading Bot Windows 설치 스크립트
REM Windows 10/11용

setlocal enabledelayedexpansion

echo ================================
echo   Trading Bot v1.0 설치 스크립트
echo   Windows 버전
echo ================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [오류] 관리자 권한으로 실행해주세요!
    echo 스크립트를 마우스 오른쪽 클릭 후 "관리자 권한으로 실행"을 선택하세요.
    pause
    exit /b 1
)

REM Python 설치 확인
echo [1/6] Python 설치 확인...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

REM Python 버전 확인
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python 버전: %PYTHON_VERSION%

REM pip 설치 확인
echo [2/6] pip 설치 확인...
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo pip 설치 중...
    python -m ensurepip --upgrade
)

REM 가상환경 생성
echo [3/6] 가상환경 생성...
if exist venv (
    echo 기존 가상환경이 발견되었습니다.
    set /p DELETE_VENV="기존 가상환경을 삭제하고 새로 만들까요? (Y/N): "
    if /i "!DELETE_VENV!"=="Y" (
        rmdir /s /q venv
        python -m venv venv
    )
) else (
    python -m venv venv
)

REM 가상환경 활성화
echo [4/6] 가상환경 활성화...
call venv\Scripts\activate.bat

REM pip 업그레이드
echo pip 업그레이드...
python -m pip install --upgrade pip

REM 의존성 설치
echo [5/6] Python 패키지 설치...
pip install -r requirements.txt

REM 환경설정 파일 생성
echo [6/6] 환경설정 파일 생성...
if not exist .env (
    copy .env.example .env
    echo .env 파일이 생성되었습니다.
) else (
    echo .env 파일이 이미 존재합니다.
)

REM 디렉토리 생성
if not exist logs mkdir logs
if not exist data mkdir data

echo.
echo ================================
echo   설치 완료!
echo ================================
echo.
echo 다음 단계를 진행하세요:
echo.
echo 1. .env 파일을 열어 API 키와 설정을 입력하세요
echo    notepad .env
echo.
echo 2. 봇 실행:
echo    run.bat
echo.
echo 3. 웹 인터페이스 접속:
echo    http://localhost:8000
echo.
echo 4. 트레이딩뷰 웹훅 URL:
echo    http://YOUR_SERVER_IP:8000/webhook/tradingview
echo.
echo Happy Trading! 
echo.
pause
