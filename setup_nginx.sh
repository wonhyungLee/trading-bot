#!/bin/bash
echo "======================================"
echo "   Trading Bot Nginx 설정 스크립트"
echo "======================================"

# 1. Nginx 설치
echo "1. Nginx 설치 중..."
sudo apt update
sudo apt install nginx -y

# 2. Nginx 시작
sudo systemctl start nginx
sudo systemctl enable nginx

# 3. 방화벽 설정
echo "2. 방화벽 설정 중..."
sudo ufw allow 'Nginx Full'

# 4. 서버 IP 주소 확인
SERVER_IP=$(curl -s ifconfig.me)
echo "서버 IP: $SERVER_IP"

# 5. Nginx 설정 파일 생성
echo "3. Nginx 설정 파일 생성 중..."
sudo tee /etc/nginx/sites-available/trading-bot > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_IP;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /webhook/tradingview {
        proxy_pass http://127.0.0.1:8000/webhook/tradingview;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 6. 설정 파일 활성화
sudo ln -s /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 7. Nginx 설정 테스트
sudo nginx -t

# 8. Nginx 재시작
sudo systemctl restart nginx

# 9. 상태 확인
sudo systemctl status nginx

echo ""
echo "======================================"
echo "   Nginx 설정 완료!"
echo "======================================"
echo ""
echo "이제 다음 URL로 접속하세요:"
echo "• 웹 대시보드: http://$SERVER_IP"
echo "• 트레이딩뷰 웹훅: http://$SERVER_IP/webhook/tradingview"
echo ""
echo "트레이딩봇을 8000번 포트에서 실행하세요:"
echo "cd ~/trading-bot"
echo "source venv/bin/activate"
echo "python app.py"
echo ""
