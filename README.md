# Trading Bot

자동 매매를 위한 트레이딩 봇입니다. 트레이딩뷰 웹훅 시그널을 받아 한국투자증권(KIS) 및 여러 거래소에서 자동으로 주문을 실행합니다.

## 주요 기능

1. **다중 계좌 지원**
   - KIS 계좌 최대 50개 지원 (KIS1 ~ KIS50)
   - 5개 거래소 지원: Binance, Upbit, Bybit, OKX, Bitget

2. **트레이딩뷰 웹훅 연동**
   - 트레이딩뷰 알람에서 웹훅 시그널 수신
   - 자동 매수/매도/포지션 청산

3. **디스코드 통합**
   - 모든 거래 활동 실시간 알림
   - 디스코드 명령어로 계좌 관리 가능
   - 디스코드 봇 지원 (선택사항)

4. **웹 대시보드**
   - 계좌 현황 모니터링
   - API 키 관리
   - 실시간 상태 확인

## 설치 방법

### 1. 요구사항
- Python 3.8 이상
- Docker (선택사항)

### 2. 기본 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/trading-bot.git
cd trading-bot

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경설정 파일 생성
cp .env.example .env
```

### 3. 환경설정

`.env` 파일을 열어 필요한 정보를 입력하세요:

```env
# 필수 설정
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# 선택 설정
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN  # 디스코드 봇 사용시
WEBHOOK_SECRET=your_secret_key     # 보안 강화시
```

### 4. 실행

#### 웹 서버만 실행
```bash
python app.py
```

#### 디스코드 봇 포함 실행
```bash
python run.py
```

#### Docker로 실행
```bash
docker-compose up -d
```

## 사용 방법

### 1. 웹 인터페이스

브라우저에서 `http://localhost:8000` 접속

- **대시보드**: 전체 계좌 현황 및 상태 확인
- **설정**: API 키 및 계좌 정보 관리

### 2. 트레이딩뷰 웹훅 설정

트레이딩뷰 알람에서 웹훅 URL 설정:
```
http://your-server:8000/webhook/tradingview
```

웹훅 메시지 형식:
```json
{
    "ticker": "AAPL",          // 종목 코드
    "action": "buy",           // buy, sell, close
    "quantity": 10,            // 수량
    "price": 150.00,          // 가격 (시장가는 0)
    "exchange": "nasdaq",      // 거래소
    "account": "kis1",         // 계좌 (kis1~kis50, binance 등)
    "order_type": "market",    // market, limit
    "strategy": "My Strategy"  // 전략 이름
}
```

### 3. 디스코드 명령어

#### 웹훅을 통한 명령어 (기본)
```
!add_kis 1 key:YOUR_KEY secret:YOUR_SECRET account:계좌번호 code:상품코드
!update_kis 1 key:NEW_KEY
!delete_kis 1
!list_kis
!status
!help
```

#### 디스코드 봇 명령어 (봇 설정시)
```
!add_kis 1 key:YOUR_KEY secret:YOUR_SECRET account:계좌번호 code:상품코드
!add_exchange binance key:YOUR_KEY secret:YOUR_SECRET
!list_kis
!status
!help_trading
```

## API 엔드포인트

### KIS 계좌 관리
- `POST /api/kis/add` - 계좌 추가/수정
- `DELETE /api/kis/delete/<number>` - 계좌 삭제

### 거래소 API 관리
- `POST /api/exchange/update` - API 키 업데이트

### 시스템
- `GET /api/status` - 시스템 상태 조회
- `GET /api/test-discord` - 디스코드 연결 테스트

## 보안 주의사항

1. **API 키 보호**
   - `.env` 파일을 절대 공개 저장소에 업로드하지 마세요
   - `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

2. **웹훅 보안**
   - `WEBHOOK_SECRET` 설정으로 웹훅 시그니처 검증
   - HTTPS 사용 권장

3. **접근 제어**
   - 프로덕션 환경에서는 IP 화이트리스트 설정
   - 방화벽으로 불필요한 포트 차단

## 🚨 웹훅 수신 및 디스코드 반응 문제 해결

### 🔧 원클릭 자동 수정
```bash
# 모든 문제를 자동으로 감지하고 수정
quick_fix.bat
```

### 🔍 상세 진단
```bash
# 전체 시스템 진단 (권장)
python debug_webhook_full.py
```

### 📋 단계별 문제 해결
자세한 해결 방법은 **TROUBLESHOOTING.md** 파일을 참고하세요.

### 🛠️ 주요 해결 도구들

#### 1. 디스코드 웹훅 설정
```bash
# 디스코드 설정 가이드 확인
type DISCORD_SETUP.md
```

#### 2. 방화벽 자동 설정
```bash
# 관리자 권한으로 실행
setup_firewall.bat
```

#### 3. 웹훅 테스트 서버
```bash
# 간단한 테스트 서버 실행
python test_webhook_server.py
```

### ⚠️ 일반적인 문제들

#### 🔴 웹훅이 수신되지 않는 경우
1. **서버 미실행**: `run.bat` 실행 확인
2. **포트 차단**: 방화벽에서 포트 8000 허용
3. **잘못된 URL**: 트레이딩뷰에서 정확한 웹훅 URL 설정
   ```
   http://YOUR_SERVER_IP:8000/webhook/tradingview
   ```
4. **네트워크 접근 불가**: 외부에서 서버 접근 불가능

#### 🔴 디스코드 알림이 오지 않는 경우
1. **웹훅 URL 미설정**: `.env` 파일에서 `DISCORD_WEBHOOK_URL` 설정
2. **잘못된 웹훅 URL**: 디스코드에서 올바른 웹훅 URL 복사
3. **권한 부족**: 디스코드 채널에서 웹훅 권한 확인
4. **네트워크 문제**: Discord API 접근 차단

#### 🔴 서버가 시작되지 않는 경우
1. **가상환경 없음**: `python -m venv venv` 실행
2. **패키지 미설치**: `pip install -r requirements.txt` 실행
3. **포트 충돌**: 다른 프로그램이 포트 8000 사용 중
4. **권한 문제**: 관리자 권한으로 실행

### 📞 추가 지원

문제가 지속되는 경우:
1. `debug_webhook_full.py` 실행 결과 확인
2. `trading_bot.log` 파일의 오류 메시지 확인  
3. `TROUBLESHOOTING.md`의 전체 체크리스트 수행

## 문제 해결

### 1. KIS API 연결 실패
- API 키가 올바른지 확인
- 계좌번호와 상품코드가 정확한지 확인
- KIS 개발자센터에서 API 사용 승인 확인

### 2. 디스코드 메시지 전송 실패
- 웹훅 URL이 올바른지 확인
- 디스코드 서버 설정에서 웹훅 권한 확인

### 3. 트레이딩뷰 웹훅 수신 실패
- 서버가 외부에서 접근 가능한지 확인
- 방화벽에서 웹훅 포트(기본 8000) 허용
- 웹훅 메시지 JSON 형식 확인

## 라이선스

MIT License

## 기여

Pull Request와 Issue를 환영합니다!
