#!/usr/bin/env python
"""
Trading Bot 상태 체크 스크립트
설정과 연결 상태를 확인합니다.
"""

import os
import sys
from dotenv import load_dotenv
from config_manager import ConfigManager
import requests
import json
from colorama import init, Fore, Style

# Windows에서 색상 지원
init()

def print_header(text):
    print(f"\n{Fore.BLUE}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def print_status(name, status, details=""):
    if status == "OK":
        status_color = Fore.GREEN
        status_symbol = "✓"
    elif status == "WARNING":
        status_color = Fore.YELLOW
        status_symbol = "!"
    else:
        status_color = Fore.RED
        status_symbol = "✗"
    
    print(f"{name:<30} [{status_color}{status_symbol} {status}{Style.RESET_ALL}] {details}")

def check_env_file():
    """환경설정 파일 확인"""
    print_header("환경설정 파일 체크")
    
    if os.path.exists('.env'):
        print_status(".env 파일", "OK", "파일이 존재합니다")
        load_dotenv()
        return True
    else:
        print_status(".env 파일", "ERROR", "파일이 없습니다. .env.example을 참고하세요")
        return False

def check_discord_webhook():
    """디스코드 웹훅 확인"""
    print_header("디스코드 웹훅 체크")
    
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    if not webhook_url:
        print_status("디스코드 웹훅", "WARNING", "URL이 설정되지 않았습니다")
        return
    
    try:
        # 테스트 메시지 전송
        response = requests.post(webhook_url, json={
            "content": "🧪 Trading Bot 연결 테스트",
            "username": "Trading Bot"
        })
        
        if response.status_code == 204:
            print_status("디스코드 웹훅", "OK", "연결 성공")
        else:
            print_status("디스코드 웹훅", "ERROR", f"응답 코드: {response.status_code}")
    except Exception as e:
        print_status("디스코드 웹훅", "ERROR", str(e))

def check_kis_accounts():
    """KIS 계좌 설정 확인"""
    print_header("KIS 계좌 설정 체크")
    
    config_manager = ConfigManager()
    accounts = config_manager.get_kis_accounts()
    
    active_count = 0
    for account in accounts:
        if account['active']:
            active_count += 1
            print_status(f"KIS{account['number']}", "OK", 
                        f"계좌: {account['account_number'][:4]}****")
        elif any([account['key'], account['secret'], account['account_number']]):
            print_status(f"KIS{account['number']}", "WARNING", "불완전한 설정")
    
    if active_count == 0:
        print_status("활성 KIS 계좌", "WARNING", "활성 계좌가 없습니다")
    else:
        print_status("활성 KIS 계좌", "OK", f"{active_count}개")

def check_exchange_apis():
    """거래소 API 설정 확인"""
    print_header("거래소 API 설정 체크")
    
    exchanges = ['BINANCE', 'UPBIT', 'BYBIT', 'OKX', 'BITGET']
    
    for exchange in exchanges:
        key = os.getenv(f'{exchange}_KEY', '')
        secret = os.getenv(f'{exchange}_SECRET', '')
        
        if key and secret:
            print_status(exchange, "OK", "API 키 설정됨")
        else:
            print_status(exchange, "WARNING", "API 키 미설정")

def check_server_config():
    """서버 설정 확인"""
    print_header("서버 설정 체크")
    
    port = os.getenv('PORT', '8000')
    webhook_secret = os.getenv('WEBHOOK_SECRET', '')
    
    print_status("서버 포트", "OK", f"포트 {port}")
    
    if webhook_secret:
        print_status("웹훅 시크릿", "OK", "보안 설정됨")
    else:
        print_status("웹훅 시크릿", "WARNING", "보안을 위해 설정 권장")

def check_python_packages():
    """Python 패키지 확인"""
    print_header("Python 패키지 체크")
    
    required_packages = [
        'flask', 'requests', 'ccxt', 'pandas', 'discord-webhook',
        'discord.py', 'python-dotenv', 'PyJWT'
    ]
    
    import pkg_resources
    
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            print_status(package, "OK", "설치됨")
        except:
            print_status(package, "ERROR", "설치 필요")

def main():
    print(f"{Fore.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║              Trading Bot v1.0 상태 체크                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    # 각 항목 체크
    if not check_env_file():
        print(f"\n{Fore.RED}환경설정 파일이 없습니다. 설치를 먼저 진행해주세요.{Style.RESET_ALL}")
        return
    
    check_server_config()
    check_discord_webhook()
    check_kis_accounts()
    check_exchange_apis()
    check_python_packages()
    
    print(f"\n{Fore.GREEN}상태 체크 완료!{Style.RESET_ALL}")
    print("\n문제가 있는 항목은 .env 파일을 수정하거나 필요한 패키지를 설치하세요.")

if __name__ == "__main__":
    main()
