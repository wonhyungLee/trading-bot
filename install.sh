#!/bin/bash

# Trading Bot 설치 스크립트
# Ubuntu/Debian 기반 시스템용

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 배너 출력
show_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                               Trading Bot v1.0                              ║
║                          자동매매 트레이딩 봇 설치 스크립트                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 시스템 요구사항 확인
check_requirements() {
    log_header "시스템 요구사항 확인"
    
    # OS 확인
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "운영체제: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "운영체제: macOS"
    else
        log_error "지원하지 않는 운영체제입니다."
        exit 1
    fi
    
    # Python 확인
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python 버전: $PYTHON_VERSION"
        
        # Python 3.8 이상 확인
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_info "Python 버전 요구사항 충족"
        else
            log_error "Python 3.8 이상이 필요합니다."
            exit 1
        fi
    else
        log_error "Python3가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # pip 확인
    if command -v pip3 &> /dev/null; then
        log_info "pip3 사용 가능"
    else
        log_error "pip3가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # Git 확인
    if command -v git &> /dev/null; then
        log_info "Git 사용 가능"
    else
        log_warn "Git이 설치되어 있지 않습니다. 수동으로 파일을 다운로드해야 합니다."
    fi
}

# 시스템 의존성 설치
install_system_dependencies() {
    log_header "시스템 의존성 설치"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            log_info "패키지 목록 업데이트..."
            sudo apt-get update
            
            log_info "필수 패키지 설치..."
            sudo apt-get install -y \
                python3-pip \
                python3-venv \
                python3-dev \
                build-essential \
                libssl-dev \
                libffi-dev \
                curl \
                wget \
                unzip
                
        # CentOS/RHEL/Fedora
        elif command -v yum &> /dev/null; then
            log_info "필수 패키지 설치..."
            sudo yum install -y \
                python3-pip \
                python3-devel \
                gcc \
                openssl-devel \
                libffi-devel \
                curl \
                wget \
                unzip
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            log_info "Homebrew로 의존성 설치..."
            brew install python3 curl wget
        else
            log_warn "Homebrew가 설치되어 있지 않습니다. 수동으로 의존성을 설치해주세요."
        fi
    fi
}

# 프로젝트 디렉토리 생성
create_project_directory() {
    log_header "프로젝트 디렉토리 설정"
    
    PROJECT_DIR="$HOME/trading-bot"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_warn "프로젝트 디렉토리가 이미 존재합니다: $PROJECT_DIR"
        read -p "기존 디렉토리를 삭제하고 새로 설치하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
            log_info "기존 디렉토리 삭제됨"
        else
            log_info "기존 디렉토리 사용"
            return
        fi
    fi
    
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    log_info "프로젝트 디렉토리 생성: $PROJECT_DIR"
}

# 가상환경 설정
setup_virtual_environment() {
    log_header "Python 가상환경 설정"
    
    log_info "가상환경 생성..."
    python3 -m venv .venv
    
    log_info "가상환경 활성화..."
    source .venv/bin/activate
    
    log_info "pip 업그레이드..."
    pip install --upgrade pip
    
    log_info "가상환경 설정 완료"
}

# Python 의존성 설치
install_python_dependencies() {
    log_header "Python 의존성 설치"
    
    log_info "requirements.txt에서 의존성 설치..."
    pip install -r requirements.txt
    
    log_info "Python 의존성 설치 완료"
}

# 환경설정 파일 생성
create_config_files() {
    log_header "환경설정 파일 생성"
    
    if [ ! -f ".env" ]; then
        log_info ".env 파일 생성..."
        cat > .env << 'EOF'
# Trading Bot Configuration
PASSWORD="dldnjsgud"

# Exchange API Keys
BINANCE_KEY=""
BINANCE_SECRET=""

UPBIT_KEY=""
UPBIT_SECRET=""

BYBIT_KEY=""
BYBIT_SECRET=""

OKX_KEY=""
OKX_SECRET=""
OKX_PASSPHRASE=""

BITGET_KEY=""
BITGET_SECRET=""
BITGET_PASSPHRASE=""

BITGET_DEMO_MODE="true"
BITGET_DEMO_KEY=""
BITGET_DEMO_SECRET=""
BITGET_DEMO_PASSPHRASE=""

# KIS Accounts (1-50)
KIS1_KEY=""
KIS1_SECRET=""
KIS1_ACCOUNT_NUMBER=""
KIS1_ACCOUNT_CODE=""

# Network Configuration
WHITELIST=["127.0.0.1", ""]
DISCORD_WEBHOOK_URL=""
PORT="8000"

# Database Configuration
DB_ID="admin@admin.com"
DB_PASSWORD="admin123!@#"

# TradingView Webhook Secret
WEBHOOK_SECRET="tradingview_webhook_secret_2024"
EOF
        log_info ".env 파일이 생성되었습니다."
    else
        log_info ".env 파일이 이미 존재합니다."
    fi
}

# 서비스 파일 생성 (systemd)
create_service_file() {
    log_header "시스템 서비스 설정"
    
    read -p "시스템 서비스로 등록하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi
    
    SERVICE_FILE="/etc/systemd/system/trading-bot.service"
    
    log_info "서비스 파일 생성: $SERVICE_FILE"
    
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PWD
Environment=PATH=$PWD/.venv/bin
ExecStart=$PWD/.venv/bin/python $PWD/run.py
Restart=on-failure
RestartSec=5

# 로그 설정
StandardOutput=append:$PWD/logs/trading-bot.log
StandardError=append:$PWD/logs/trading-bot-error.log

[Install]
WantedBy=multi-user.target
EOF

    # 로그 디렉토리 생성
    mkdir -p logs
    
    # 서비스 등록
    sudo systemctl daemon-reload
    sudo systemctl enable trading-bot.service
    
    log_info "서비스가 등록되었습니다."
    log_info "서비스 시작: sudo systemctl start trading-bot"
    log_info "서비스 상태: sudo systemctl status trading-bot"
}

# 방화벽 설정
configure_firewall() {
    log_header "방화벽 설정"
    
    if command -v ufw &> /dev/null; then
        read -p "방화벽에서 8000번 포트를 열겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo ufw allow 8000
            log_info "방화벽에서 8000번 포트가 열렸습니다."
        fi
    else
        log_warn "ufw가 설치되어 있지 않습니다. 수동으로 방화벽을 설정해주세요."
    fi
}

# 설치 완료 메시지
show_completion_message() {
    log_header "설치 완료"
    
    echo -e "${GREEN}"
    cat << EOF
╔══════════════════════════════════════════════════════════════════════════════╗
║                               설치 완료!                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

다음 단계를 진행하세요:

1. 환경설정 파일 편집:
   nano .env

2. API 키 및 계좌 정보 입력

3. 봇 실행:
   source .venv/bin/activate
   python run.py

4. 웹 인터페이스 접속:
   http://localhost:8000

5. 트레이딩뷰 웹훅 URL:
   http://YOUR_SERVER_IP:8000/webhook/tradingview

추가 도움말:
- README.md 파일을 참조하세요
- 로그 확인: tail -f trading_bot.log
- 설정 확인: python run.py --check-config

Happy Trading! 📈
EOF
    echo -e "${NC}"
}

# 메인 설치 프로세스
main() {
    show_banner
    
    log_info "Trading Bot v1.0 설치를 시작합니다..."
    echo
    
    check_requirements
    install_system_dependencies
    create_project_directory
    setup_virtual_environment
    install_python_dependencies
    create_config_files
    create_service_file
    configure_firewall
    
    show_completion_message
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
