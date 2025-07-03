# 📱 디스코드 웹훅 설정 가이드

Trading Bot에서 디스코드로 알림을 받기 위한 설정 방법입니다.

## 1단계: 디스코드 웹훅 URL 생성

### 1. 디스코드 서버에서 채널 선택
- 알림을 받고 싶은 채널로 이동

### 2. 채널 설정 → 연동 → 웹훅
- 채널 이름 옆의 ⚙️ 버튼 클릭
- "연동" 탭 선택
- "웹훅" 선택
- "새 웹훅" 버튼 클릭

### 3. 웹훅 설정
- **이름**: Trading Bot (원하는 이름)
- **아바타**: 원하는 이미지 (선택사항)
- **웹훅 URL 복사** 버튼 클릭하여 URL 복사

## 2단계: .env 파일에 웹훅 URL 설정

### 1. .env 파일 열기
```bash
# 현재 설정
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

### 2. YOUR_WEBHOOK_ID와 YOUR_WEBHOOK_TOKEN을 실제 값으로 변경
```bash
# 예시 (실제 URL 사용)
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1234567890123456789/abcdef-ghijklmnop-qrstuvwxyz"
```

## 3단계: 설정 테스트

### 방법 1: 웹 인터페이스에서 테스트
1. Trading Bot 웹 페이지 접속: `http://localhost:8000`
2. "설정" 페이지로 이동
3. "디스코드 연결 테스트" 버튼 클릭

### 방법 2: 디버깅 스크립트로 테스트
```bash
python debug_webhook_full.py
```

### 방법 3: API 직접 호출
```bash
curl -X GET "http://localhost:8000/api/test-discord"
```

## 4단계: 웹훅 URL 보안

### ⚠️ 보안 주의사항
- 웹훅 URL은 **절대 공개하지 마세요**
- GitHub에 업로드할 때 .env 파일이 포함되지 않도록 주의
- 필요시 웹훅을 재생성하여 URL을 변경할 수 있습니다

### 안전한 관리
1. .env 파일을 .gitignore에 추가
2. 웹훅 URL을 별도의 비밀번호 관리자에 저장
3. 정기적으로 웹훅 URL 변경 고려

## 🔧 문제 해결

### 웹훅 메시지가 전송되지 않는 경우

1. **URL 형식 확인**
   ```
   올바른 형식: https://discord.com/api/webhooks/ID/TOKEN
   잘못된 형식: https://discordapp.com/... 또는 다른 형식
   ```

2. **권한 확인**
   - 해당 채널에 메시지 전송 권한이 있는지 확인
   - 웹훅이 삭제되지 않았는지 확인

3. **네트워크 확인**
   - 인터넷 연결 상태 확인
   - 방화벽이 Discord API 접근을 차단하지 않는지 확인

4. **로그 확인**
   ```bash
   # 로그 파일에서 오류 확인
   tail -f trading_bot.log | grep -i discord
   ```

## 📋 설정 완료 후 받을 수 있는 알림들

- ✅ 봇 시작/종료 알림
- 📈 거래 신호 수신 및 처리 결과
- ⚠️ 오류 및 예외 상황 알림
- 💰 계좌 정보 변경 알림
- 🔄 API 키 업데이트 알림
- 📊 정기 상태 보고서 (선택사항)

## 💡 고급 설정

### 알림 채널 분리
여러 웹훅을 설정하여 알림을 분리할 수 있습니다:
- 거래 알림용 채널
- 오류 알림용 채널  
- 상태 보고용 채널

### 알림 레벨 설정
코드를 수정하여 알림 레벨을 조정할 수 있습니다:
- 중요 알림만 (오류, 거래 완료)
- 모든 알림 (상태 변경, 디버그 정보 포함)
