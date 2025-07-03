#!/bin/bash
echo "======================================"
echo "   Trading Bot Service 등록"
echo "======================================"

# 서비스 파일 생성
sudo tee /etc/systemd/system/trading-bot.service > /dev/null <<EOF
[Unit]
Description=Trading Bot Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/trading-bot
ExecStart=/home/ubuntu/trading-bot/venv/bin/python app.py
Restart=always
RestartSec=3
Environment=PATH=/home/ubuntu/trading-bot/venv/bin

[Install]
WantedBy=multi-user.target
EOF

# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# 서비스 상태 확인
sudo systemctl status trading-bot

echo "======================================"
echo "   서비스 등록 완료!"
echo "======================================"
echo ""
echo "유용한 명령어:"
echo "• 서비스 상태: sudo systemctl status trading-bot"
echo "• 서비스 중지: sudo systemctl stop trading-bot"
echo "• 서비스 재시작: sudo systemctl restart trading-bot"
echo "• 로그 확인: sudo journalctl -u trading-bot -f"
echo ""
