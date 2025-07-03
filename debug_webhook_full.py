#!/usr/bin/env python3
"""
완전한 웹훅 디버깅 스크립트
서버 상태, 네트워크 연결, 디스코드 연결 등을 모두 테스트합니다.
"""

import os
import sys
import json
import time
import requests
import subprocess
import socket
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def check_port_open(host, port):
    """포트가 열려있는지 확인"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def get_external_ip():
    """외부 IP 주소 획득"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return "Unknown"

def test_discord_webhook():
    """디스코드 웹훅 테스트"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    if not webhook_url or webhook_url == "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN":
        return False, "❌ 디스코드 웹훅 URL이 설정되지 않았습니다."
    
    try:
        payload = {
            "content": f"🧪 **웹훅 테스트** - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "username": "Trading Bot Debug"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            return True, "✅ 디스코드 웹훅 정상 작동"
        else:
            return False, f"❌ 디스코드 웹훅 오류: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"❌ 디스코드 웹훅 오류: {str(e)}"

def test_local_webhook():
    """로컬 웹훅 테스트"""
    port = int(os.getenv('PORT', 8000))
    
    # 포트 확인
    if not check_port_open('127.0.0.1', port):
        return False, f"❌ 포트 {port}가 열려있지 않습니다. 서버가 실행 중인지 확인하세요."
    
    try:
        # 테스트 웹훅 전송
        test_data = {
            "ticker": "BTCUSDT",
            "action": "buy",
            "quantity": 0.001,
            "price": 45000,
            "exchange": "binance",
            "account": "test",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            f'http://127.0.0.1:{port}/webhook/tradingview',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, f"✅ 로컬 웹훅 정상 작동 (응답: {response.status_code})"
        else:
            return False, f"❌ 로컬 웹훅 오류: HTTP {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"❌ 로컬 웹훅 오류: {str(e)}"

def check_firewall():
    """Windows 방화벽 상태 확인"""
    try:
        port = os.getenv('PORT', 8000)
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'show', 'rule', 
            'name=all', 'dir=in', 'protocol=tcp', f'localport={port}'
        ], capture_output=True, text=True, timeout=10)
        
        if 'No rules match' in result.stdout:
            return False, f"❌ 포트 {port}에 대한 방화벽 규칙이 없습니다."
        else:
            return True, f"✅ 포트 {port}에 대한 방화벽 규칙이 존재합니다."
            
    except Exception as e:
        return False, f"❌ 방화벽 확인 오류: {str(e)}"

def main():
    """메인 디버깅 함수"""
    print("="*60)
    print("🔧 Trading Bot 웹훅 디버깅 시작")
    print("="*60)
    print()
    
    # 1. 환경 설정 확인
    print("📋 1. 환경 설정 확인")
    print("-" * 30)
    
    port = os.getenv('PORT', 8000)
    webhook_secret = os.getenv('WEBHOOK_SECRET', '')
    discord_url = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    print(f"   포트: {port}")
    print(f"   웹훅 시크릿: {'설정됨' if webhook_secret else '미설정'}")
    print(f"   디스코드 URL: {'설정됨' if discord_url and discord_url != 'https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN' else '미설정'}")
    print()
    
    # 2. 네트워크 상태 확인
    print("🌐 2. 네트워크 상태 확인")
    print("-" * 30)
    
    external_ip = get_external_ip()
    print(f"   외부 IP: {external_ip}")
    
    local_port_open = check_port_open('127.0.0.1', int(port))
    print(f"   로컬 포트 {port}: {'✅ 열림' if local_port_open else '❌ 닫힘'}")
    
    if external_ip != "Unknown":
        external_port_open = check_port_open(external_ip, int(port))
        print(f"   외부 포트 {port}: {'✅ 열림' if external_port_open else '❌ 닫힘'}")
    print()
    
    # 3. 방화벽 확인
    print("🔥 3. 방화벽 확인")
    print("-" * 30)
    
    firewall_ok, firewall_msg = check_firewall()
    print(f"   {firewall_msg}")
    print()
    
    # 4. 디스코드 웹훅 테스트
    print("💬 4. 디스코드 웹훅 테스트")
    print("-" * 30)
    
    discord_ok, discord_msg = test_discord_webhook()
    print(f"   {discord_msg}")
    print()
    
    # 5. 로컬 웹훅 테스트
    print("🔗 5. 로컬 웹훅 테스트")
    print("-" * 30)
    
    webhook_ok, webhook_msg = test_local_webhook()
    print(f"   {webhook_msg}")
    print()
    
    # 6. 결과 요약
    print("📊 6. 결과 요약")
    print("-" * 30)
    
    issues = []
    if not discord_ok:
        issues.append("디스코드 웹훅 설정")
    if not local_port_open:
        issues.append("서버 미실행")
    if not firewall_ok:
        issues.append("방화벽 설정")
    if not webhook_ok:
        issues.append("웹훅 응답")
    
    if not issues:
        print("   ✅ 모든 테스트 통과! 웹훅이 정상 작동해야 합니다.")
    else:
        print(f"   ❌ 해결 필요한 문제: {', '.join(issues)}")
    
    print()
    print("="*60)
    print("🔧 디버깅 완료")
    print("="*60)
    
    # 7. 해결 방법 제시
    if issues:
        print()
        print("💡 해결 방법:")
        print("-" * 20)
        
        if "디스코드 웹훅 설정" in issues:
            print("1. 디스코드에서 웹훅 URL을 생성하고 .env 파일에 설정하세요")
            print("   - 디스코드 서버 → 채널 설정 → 연동 → 웹훅")
            print()
        
        if "서버 미실행" in issues:
            print("2. Trading Bot 서버를 실행하세요")
            print("   - run.bat 실행 또는 python app.py")
            print()
        
        if "방화벽 설정" in issues:
            print(f"3. Windows 방화벽에서 포트 {port}을 허용하세요")
            print(f"   netsh advfirewall firewall add rule name=\"TradingBot\" dir=in action=allow protocol=TCP localport={port}")
            print()
        
        if "웹훅 응답" in issues:
            print("4. 로그를 확인하고 서버 오류를 해결하세요")
            print("   - trading_bot.log 파일 확인")
            print()

if __name__ == "__main__":
    main()
