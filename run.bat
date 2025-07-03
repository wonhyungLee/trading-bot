@echo off
REM Trading Bot 실행 스크립트

echo ================================
echo   Trading Bot v1.0 시작
echo ================================
echo.

REM 가상환경 활성화
if exist venv (
    echo 가상환경 활성화...
    call venv\Scripts\activate.bat
) else (
    echo [오류] 가상환경을 찾을 수 없습니다.
    echo install.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)

REM .env 파일 확인
if not exist .env (
    echo [오류] .env 파일을 찾을 수 없습니다.
    echo .env.example을 복사하여 .env 파일을 생성하고 설정을 입력해주세요.
    pause
    exit /b 1
)

REM 봇 실행
echo Trading Bot을 시작합니다...
echo 종료하려면 Ctrl+C를 누르세요.
echo.
python run.py

pause
