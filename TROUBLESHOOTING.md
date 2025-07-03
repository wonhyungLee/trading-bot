# 🔧 Trading Bot 웹훅 문제 해결 체크리스트

트레이딩뷰 웹훅이 수신되지 않고 디스코드 알림이 오지 않는 문제를 단계별로 해결하세요.

## ✅ 1단계: 기본 설정 확인

### 📋 .env 파일 설정 확인
- [ ] `.env` 파일이 존재하는가?
- [ ] `DISCORD_WEBHOOK_URL`이 실제 웹훅 URL로 설정되어 있는가?
- [ ] `PORT` 설정이 올바른가? (기본값: 8000)
- [ ] `WEBHOOK_SECRET`이 설정되어 있는가?

### 📱 디스코드 웹훅 설정 확인
- [ ] 디스코드 채널에 웹훅이 생성되어 있는가?
- [ ] 웹훅 URL이 정확히 복사되었는가?
- [ ] 해당 채널에 메시지 전송 권한이 있는가?

## ✅ 2단계: 서버 실행 상태 확인

### 🚀 서버 시작
```bash
# 서버 실행 (다음 중 하나)
run.bat
# 또는
python app.py
# 또는
python run.py
```

### 🔍 서버 상태 확인
- [ ] 명령 프롬프트에서 오류 없이 실행되는가?
- [ ] `http://localhost:8000`에 접속이 되는가?
- [ ] 브라우저에서 대시보드가 표시되는가?

## ✅ 3단계: 네트워크 및 방화벽 설정

### 🔥 방화벽 설정
```bash
# 관리자 권한으로 실행
setup_firewall.bat
```

### 🌐 포트 확인
```bash
# 포트가 열려있는지 확인
netstat -an | findstr ":8000"
```

### 📡 외부 접근 테스트
- [ ] 로컬에서 접근 가능한가? (`http://127.0.0.1:8000`)
- [ ] 외부 IP로 접근 가능한가? (공유기/라우터 설정 필요)

## ✅ 4단계: 디스코드 연결 테스트

### 💬 디스코드 테스트
```bash
# 방법 1: 웹 인터페이스
http://localhost:8000 → 설정 → 디스코드 연결 테스트

# 방법 2: API 직접 호출
curl -X GET "http://localhost:8000/api/test-discord"

# 방법 3: 디버깅 스크립트
python debug_webhook_full.py
```

### 📝 디스코드 테스트 결과 확인
- [ ] 디스코드 채널에 테스트 메시지가 도착했는가?
- [ ] HTTP 204 응답이 반환되었는가?
- [ ] 오류 메시지가 없는가?

## ✅ 5단계: 웹훅 수신 테스트

### 🔗 로컬 웹훅 테스트
```bash
# 방법 1: curl로 테스트
curl -X POST http://localhost:8000/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{"ticker":"BTCUSDT","action":"buy","quantity":0.001,"price":45000}'

# 방법 2: 테스트 서버 실행
python test_webhook_server.py
```

### 📊 웹훅 테스트 결과 확인
- [ ] HTTP 200 응답이 반환되었는가?
- [ ] 로그에 웹훅 수신 메시지가 기록되었는가?
- [ ] 디스코드에 거래 알림이 전송되었는가?

## ✅ 6단계: 트레이딩뷰 설정 확인

### 📈 트레이딩뷰 알림 설정
- [ ] 알림이 웹훅으로 설정되어 있는가?
- [ ] 웹훅 URL이 올바른가?
  ```
  http://YOUR_SERVER_IP:8000/webhook/tradingview
  ```
- [ ] JSON 페이로드가 올바른 형식인가?
  ```json
  {
    "ticker": "{{ticker}}",
    "action": "buy",
    "quantity": 0.001,
    "price": {{close}},
    "exchange": "binance"
  }
  ```

### 🔐 웹훅 보안 설정
- [ ] `X-Webhook-Signature` 헤더가 설정되어 있는가? (선택사항)
- [ ] WEBHOOK_SECRET과 일치하는가?

## ✅ 7단계: 로그 및 오류 확인

### 📋 로그 파일 확인
```bash
# 로그 파일 확인
type trading_bot.log
# 또는
tail -f trading_bot.log
```

### 🔍 일반적인 오류들
- [ ] `ConnectionError`: 네트워크 연결 문제
- [ ] `404 Not Found`: 웹훅 URL 오류
- [ ] `401 Unauthorized`: 시그니처 검증 실패
- [ ] `500 Internal Server Error`: 서버 내부 오류

## ✅ 8단계: 고급 디버깅

### 🔧 전체 시스템 진단
```bash
# 종합 디버깅 스크립트 실행
python debug_webhook_full.py
```

### 📡 네트워크 상세 분석
```bash
# 포트 스캔
nmap -p 8000 localhost

# 프로세스 확인
tasklist | findstr python

# 네트워크 연결 확인
netsh firewall show state
```

## 🚨 응급 해결 방법

### 🔄 서비스 재시작
```bash
# 1. 현재 실행 중인 서버 종료 (Ctrl+C)
# 2. 5초 대기
# 3. 서버 재시작
run.bat
```

### 🔧 설정 초기화
```bash
# .env 파일 백업 후 재설정
copy .env .env.backup
copy .env.example .env
# 필요한 설정들을 다시 입력
```

### 📞 외부 서비스 이용
```bash
# ngrok으로 터널링 (임시 해결책)
ngrok http 8000
# 생성된 URL을 트레이딩뷰에 설정
```

## 📞 추가 도움이 필요한 경우

1. 위 모든 단계를 수행했지만 여전히 문제가 있는 경우
2. `debug_webhook_full.py` 실행 결과를 확인
3. `trading_bot.log` 파일의 오류 메시지 확인
4. 네트워크 관리자에게 방화벽/라우터 설정 문의

## 📊 성공 확인 방법

모든 것이 정상 작동하면:
- ✅ 브라우저에서 `http://localhost:8000` 접속 가능
- ✅ 디스코드 테스트 메시지 수신 성공
- ✅ 웹훅 테스트 성공 (HTTP 200 응답)
- ✅ 트레이딩뷰 알림 발생 시 디스코드 알림 수신
- ✅ 로그 파일에 정상 메시지 기록
