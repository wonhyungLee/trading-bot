#!/usr/bin/env python
"""
Trading Bot 메인 실행 파일
웹 서버와 디스코드 봇을 동시에 실행합니다.
"""

import os
import sys
import subprocess
import signal
import time
import logging
from multiprocessing import Process
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 프로세스 저장용
processes = []

def run_web_server():
    """Flask 웹 서버 실행"""
    logging.info("Starting web server...")
    subprocess.run([sys.executable, "app.py"])

def run_discord_bot():
    """디스코드 봇 실행"""
    if os.getenv('DISCORD_BOT_TOKEN'):
        logging.info("Starting Discord bot...")
        subprocess.run([sys.executable, "discord_bot.py"])
    else:
        logging.info("Discord bot token not found. Skipping bot startup.")

def signal_handler(sig, frame):
    """종료 시그널 처리"""
    logging.info("Shutting down Trading Bot...")
    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()
    sys.exit(0)

def main():
    """메인 실행 함수"""
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logging.info("=== Trading Bot Starting ===")
    
    # 웹 서버 프로세스 시작
    web_process = Process(target=run_web_server)
    web_process.start()
    processes.append(web_process)
    
    # 잠시 대기 (웹 서버 시작 시간)
    time.sleep(2)
    
    # 디스코드 봇 프로세스 시작 (토큰이 있는 경우)
    if os.getenv('DISCORD_BOT_TOKEN'):
        bot_process = Process(target=run_discord_bot)
        bot_process.start()
        processes.append(bot_process)
    
    logging.info("=== All services started ===")
    logging.info(f"Web interface: http://localhost:{os.getenv('PORT', 8000)}")
    logging.info("Press Ctrl+C to stop")
    
    # 프로세스들이 종료될 때까지 대기
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
