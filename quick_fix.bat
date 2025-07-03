@echo off
REM Trading Bot 원클릭 수정 스크립트
REM 주요 문제들을 자동으로 감지하고 수정합니다

setlocal EnableDelayedExpansion

echo ================================
echo   Trading Bot 원클릭 수정
echo ================================
echo.

REM 1. .env 파일 확인
echo 📋 1. 설정 파일 확인 중...
if not exist .env (
    echo ❌ .env 파일이 없습니다. .env.example에서 복사합니다...
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ .env 파일이 생성되었습니다.
    ) else (
        echo ❌ .env.example 파일도 없습니다!
        goto :error
    )
) else (
    echo ✅ .env 파일 존재함
)

REM 2. 디스코드 웹훅 URL 확인
echo.
echo 💬 2. 디스코드 웹훅 설정 확인 중...
findstr /i "DISCORD_WEBHOOK_URL" .env | findstr /v "YOUR_WEBHOOK" >nul
if !errorLevel! neq 0 (
    echo ❌ 디스코드 웹훅 URL이 설정되지 않았습니다.
    echo.
    echo 💡 디스코드 웹훅 설정 방법:
    echo    1. 디스코드 채널 설정 → 연동 → 웹훅
    echo    2. 웹훅 URL 복사
    echo    3. .env 파일의 DISCORD_WEBHOOK_URL에 붙여넣기
    echo.
    set /p webhook_url="디스코드 웹훅 URL을 입력하세요 (또는 Enter로 건너뛰기): "
    if "!webhook_url!" neq "" (
        echo DISCORD_WEBHOOK_URL="!webhook_url!" >> .env.temp
        findstr /v "DISCORD_WEBHOOK_URL" .env >> .env.temp
        move .env.temp .env >nul
        echo ✅ 디스코드 웹훅 URL이 설정되었습니다.
    )
) else (
    echo ✅ 디스코드 웹훅 URL 설정됨
)

REM 3. 가상환경 확인
echo.
echo 🐍 3. Python 가상환경 확인 중...
if exist venv (
    echo ✅ 가상환경 존재함
) else (
    echo ❌ 가상환경이 없습니다. 생성 중...
    python -m venv venv
    if !errorLevel! == 0 (
        echo ✅ 가상환경이 생성되었습니다.
    ) else (
        echo ❌ 가상환경 생성 실패. Python이 설치되어 있는지 확인하세요.
        goto :error
    )
)

REM 4. 의존성 설치
echo.
echo 📦 4. 의존성 패키지 확인 중...
call venv\Scripts\activate.bat
pip list | findstr flask >nul
if !errorLevel! neq 0 (
    echo ❌ 필요한 패키지가 설치되지 않았습니다. 설치 중...
    pip install -r requirements.txt
    if !errorLevel! == 0 (
        echo ✅ 패키지 설치 완료
    ) else (
        echo ❌ 패키지 설치 실패
        goto :error
    )
) else (
    echo ✅ 필요한 패키지 설치됨
)

REM 5. 포트 확인
echo.
echo 🔍 5. 포트 상태 확인 중...
netstat -an | findstr ":8000" >nul
if !errorLevel! == 0 (
    echo ⚠️ 포트 8000이 이미 사용 중입니다.
    echo 💡 기존 프로세스를 종료하거나 다른 포트를 사용하세요.
) else (
    echo ✅ 포트 8000 사용 가능
)

REM 6. 방화벽 규칙 확인 (관리자 권한 필요)
echo.
echo 🔥 6. 방화벽 규칙 확인 중...
netsh advfirewall firewall show rule name="TradingBot-HTTP" >nul 2>&1
if !errorLevel! neq 0 (
    echo ❌ 방화벽 규칙이 없습니다.
    echo 💡 관리자 권한으로 setup_firewall.bat을 실행하세요.
) else (
    echo ✅ 방화벽 규칙 존재함
)

REM 7. 서버 테스트 시작
echo.
echo 🚀 7. 서버 테스트 시작...
echo 서버를 5초간 실행하여 정상 작동을 확인합니다...

REM 백그라운드에서 서버 시작
start /B python app.py >server_test.log 2>&1

REM 5초 대기
timeout /t 5 /nobreak >nul

REM 서버 응답 확인
echo 🔍 서버 응답 확인 중...
curl -s http://localhost:8000 >nul 2>&1
if !errorLevel! == 0 (
    echo ✅ 서버가 정상적으로 실행 중입니다!
    
    REM 디스코드 테스트
    echo 💬 디스코드 연결 테스트 중...
    curl -s http://localhost:8000/api/test-discord >nul 2>&1
    if !errorLevel! == 0 (
        echo ✅ 디스코드 연결 테스트 완료
    ) else (
        echo ⚠️ 디스코드 연결 테스트 실패 (웹훅 URL 확인 필요)
    )
    
) else (
    echo ❌ 서버가 응답하지 않습니다.
    echo 💡 server_test.log 파일을 확인하세요.
)

REM 테스트 서버 종료
taskkill /f /im python.exe >nul 2>&1

echo.
echo ================================
echo   수정 작업 완료!
echo ================================
echo.

REM 8. 최종 안내
echo 💡 다음 단계:
echo    1. 모든 설정이 완료되었습니다.
echo    2. run.bat을 실행하여 Trading Bot을 시작하세요.
echo    3. 브라우저에서 http://localhost:8000에 접속하세요.
echo    4. 트레이딩뷰에서 웹훅 URL을 다음과 같이 설정하세요:
echo       http://YOUR_SERVER_IP:8000/webhook/tradingview
echo.

if exist server_test.log (
    echo 📋 서버 테스트 로그:
    echo ----------------------------------------
    type server_test.log
    echo ----------------------------------------
    del server_test.log
)

echo.
set /p start_server="지금 Trading Bot을 시작하시겠습니까? (y/n): "
if /i "!start_server!" == "y" (
    echo.
    echo 🚀 Trading Bot을 시작합니다...
    run.bat
) else (
    echo.
    echo 👋 준비가 완료되었습니다! run.bat을 실행하여 시작하세요.
)

goto :end

:error
echo.
echo ❌ 수정 작업 중 오류가 발생했습니다.
echo 💡 TROUBLESHOOTING.md 파일을 참고하여 수동으로 해결하세요.

:end
pause
