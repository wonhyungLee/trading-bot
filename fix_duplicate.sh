#!/bin/bash
echo "======================================"
echo "   중복 함수 제거 스크립트"
echo "======================================"

# 1. 백업 생성
cp app.py app.py.backup_$(date +%Y%m%d_%H%M%S)

# 2. 중복된 함수 찾기
echo "중복된 함수 확인:"
grep -n "def tradingview_webhook" app.py
echo ""
grep -n "@app.route.*webhook.*tradingview" app.py
echo ""

# 3. 파일에서 268번째 줄 이후의 중복 부분 확인
echo "268번째 줄 이후 내용:"
tail -n +268 app.py | head -50
echo ""

# 4. 임시 해결: 중복된 부분 제거 (268번째 줄 이후 삭제)
echo "중복 부분 제거 중..."
head -n 267 app.py > app_fixed.py

# 5. app.py의 마지막 부분 추가 (main 함수)
cat >> app_fixed.py << 'EOF'

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

def verify_webhook_signature(payload, signature, secret):
    """웹훅 시그니처 검증"""
    if not signature or not secret:
        return True  # 시크릿이 설정되지 않은 경우 통과
    
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    except Exception as e:
        logging.error(f"Signature verification error: {e}")
        return False

if __name__ == '__main__':
    # 시작 시 디스코드 알림
    discord_webhook.send_message(
        f"🚀 **Trading Bot이 시작되었습니다!**\n"
        f"• 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"• 서버 포트: {os.getenv('PORT', '80')}\n"
        f"• 봇 버전: v1.0"
    )
    
    # Flask 앱 실행
    port = int(os.getenv('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# 6. 수정된 파일로 교체
mv app_fixed.py app.py

echo "======================================"
echo "   수정 완료!"
echo "======================================"
echo ""
echo "수정된 app.py로 교체되었습니다."
echo "이제 다시 실행해보세요: sudo python app.py"
echo ""
