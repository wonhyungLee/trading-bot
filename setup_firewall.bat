@echo off
REM Trading Bot 방화벽 설정 스크립트
REM 관리자 권한으로 실행해야 합니다

echo ================================
echo   Trading Bot 방화벽 설정
echo ================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 관리자 권한 확인됨
) else (
    echo ❌ 관리자 권한이 필요합니다!
    echo 이 스크립트를 우클릭하여 "관리자 권한으로 실행"을 선택하세요.
    pause
    exit /b 1
)

echo.

REM .env 파일에서 포트 읽기
set PORT=8000
if exist .env (
    for /f "tokens=2 delims==" %%a in ('findstr /i "PORT" .env') do (
        set PORT=%%a
        set PORT=!PORT:"=!
    )
)

echo 📍 포트: %PORT%
echo.

REM 기존 규칙 삭제 (있다면)
echo 🗑️ 기존 방화벽 규칙 삭제 중...
netsh advfirewall firewall delete rule name="TradingBot-HTTP" >nul 2>&1
netsh advfirewall firewall delete rule name="TradingBot-HTTPS" >nul 2>&1

REM 새 방화벽 규칙 추가
echo 🔥 방화벽 규칙 추가 중...

REM HTTP 포트 허용
netsh advfirewall firewall add rule name="TradingBot-HTTP" dir=in action=allow protocol=TCP localport=%PORT%
if %errorLevel% == 0 (
    echo ✅ HTTP 포트 %PORT% 허용 규칙 추가됨
) else (
    echo ❌ HTTP 포트 %PORT% 규칙 추가 실패
)

REM HTTPS 포트도 허용 (필요한 경우)
if "%PORT%" neq "443" (
    netsh advfirewall firewall add rule name="TradingBot-HTTPS" dir=in action=allow protocol=TCP localport=443
    if %errorLevel% == 0 (
        echo ✅ HTTPS 포트 443 허용 규칙 추가됨
    ) else (
        echo ❌ HTTPS 포트 443 규칙 추가 실패
    )
)

echo.

REM 현재 방화벽 규칙 확인
echo 📋 현재 방화벽 규칙 확인:
netsh advfirewall firewall show rule name="TradingBot-HTTP"
echo.

REM 포트 상태 확인
echo 🔍 포트 상태 확인:
netstat -an | findstr ":%PORT%"
echo.

echo ================================
echo   방화벽 설정 완료!
echo ================================
echo.
echo 💡 추가 확인사항:
echo   1. 라우터/공유기에서 포트 포워딩 설정
echo   2. 클라우드 서버인 경우 보안 그룹 설정
echo   3. 안티바이러스 소프트웨어 방화벽 확인
echo.

pause
