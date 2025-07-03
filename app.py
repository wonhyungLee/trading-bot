import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import hashlib
import hmac

from config_manager import ConfigManager
from discord_webhook import DiscordWebhook
from trading_engine import TradingEngine

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

# Flask 앱 초기화
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tradingbot_secret_key_2024')
CORS(app)

# 컴포넌트 초기화
config_manager = ConfigManager()
discord_webhook = DiscordWebhook(config_manager)
trading_engine = TradingEngine(config_manager, discord_webhook)

@app.route('/')
def index():
    """메인 대시보드 페이지"""
    try:
        # 계좌 정보 가져오기
        kis_accounts = config_manager.get_kis_accounts()
        portfolio_status = trading_engine.get_portfolio_status()
        
        return render_template('dashboard.html', 
                             kis_accounts=kis_accounts,
                             portfolio_status=portfolio_status)
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        flash(f"대시보드 로드 중 오류가 발생했습니다: {str(e)}", 'error')
        return render_template('dashboard.html', kis_accounts=[], portfolio_status={})

@app.route('/config')
def config_page():
    """설정 페이지"""
    kis_accounts = config_manager.get_kis_accounts()
    discord_url = config_manager.get_discord_webhook_url()
    webhook_secret = config_manager.get_webhook_secret()
    
    exchanges = {}
    for exchange in ['binance', 'upbit', 'bybit', 'okx', 'bitget']:
        exchanges[exchange] = config_manager.get_exchange_config(exchange)
    
    return render_template('config.html',
                         kis_accounts=kis_accounts,
                         exchanges=exchanges,
                         discord_url=discord_url,
                         webhook_secret=webhook_secret)

@app.route('/api/kis/add', methods=['POST'])
def add_kis_account():
    """KIS 계좌 추가/수정"""
    try:
        data = request.json
        account_number = int(data.get('account_number'))
        key = data.get('key', '').strip()
        secret = data.get('secret', '').strip()
        acc_number = data.get('acc_number', '').strip()
        acc_code = data.get('acc_code', '').strip()
        
        if not (1 <= account_number <= 50):
            return jsonify({'success': False, 'error': '계좌 번호는 1~50 사이여야 합니다.'})
        
        success = config_manager.update_kis_account(
            account_number, key, secret, acc_number, acc_code
        )
        
        if success:
            # 클라이언트 새로고침
            trading_engine.refresh_clients()
            
            # 디스코드 알림
            discord_webhook.send_message(
                f"✅ **KIS{account_number} 계좌가 {'업데이트' if any([key, secret, acc_number, acc_code]) else '추가'}되었습니다.**\n"
                f"• 계좌번호: {acc_number}\n"
                f"• 상품코드: {acc_code}\n"
                f"• 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return jsonify({'success': True, 'message': f'KIS{account_number} 계좌가 성공적으로 저장되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '계좌 정보 저장에 실패했습니다.'})
            
    except Exception as e:
        logging.error(f"Add KIS account error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/kis/delete/<int:account_number>', methods=['DELETE'])
def delete_kis_account(account_number):
    """KIS 계좌 삭제"""
    try:
        if not (1 <= account_number <= 50):
            return jsonify({'success': False, 'error': '잘못된 계좌 번호입니다.'})
        
        success = config_manager.delete_kis_account(account_number)
        
        if success:
            # 클라이언트 새로고침
            trading_engine.refresh_clients()
            
            # 디스코드 알림
            discord_webhook.send_message(
                f"🗑️ **KIS{account_number} 계좌가 삭제되었습니다.**\n"
                f"• 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return jsonify({'success': True, 'message': f'KIS{account_number} 계좌가 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '계좌 삭제에 실패했습니다.'})
            
    except Exception as e:
        logging.error(f"Delete KIS account error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/update', methods=['POST'])
def update_exchange():
    """거래소 API 키 업데이트"""
    try:
        data = request.json
        exchange = data.get('exchange', '').lower()
        
        if exchange not in ['binance', 'upbit', 'bybit', 'okx', 'bitget']:
            return jsonify({'success': False, 'error': '지원하지 않는 거래소입니다.'})
        
        kwargs = {}
        for field in ['key', 'secret', 'passphrase']:
            value = data.get(field, '').strip()
            if value:
                kwargs[field] = value
        
        if exchange == 'bitget' and 'demo' in data:
            kwargs['demo'] = data['demo']
        
        success = config_manager.update_exchange_config(exchange, **kwargs)
        
        if success:
            # 클라이언트 새로고침
            trading_engine.refresh_clients()
            
            # 디스코드 알림
            discord_webhook.send_message(
                f"🔄 **{exchange.upper()} API 키가 업데이트되었습니다.**\n"
                f"• 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return jsonify({'success': True, 'message': f'{exchange.upper()} API 키가 업데이트되었습니다.'})
        else:
            return jsonify({'success': False, 'error': 'API 키 업데이트에 실패했습니다.'})
            
    except Exception as e:
        logging.error(f"Update exchange error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/discord/update', methods=['POST'])
def update_discord_webhook():
    """디스코드 웹훅 URL 업데이트"""
    try:
        data = request.json
        url = data.get('url', '').strip()
        
        success = config_manager.update_discord_webhook_url(url)
        
        if success:
            # 새 웹훅으로 테스트 메시지 전송
            discord_webhook.webhook_url = url
            discord_webhook.send_message(
                f"✅ **디스코드 웹훅이 성공적으로 연결되었습니다!**\n"
                f"• 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"• 봇이 이제 이 채널로 알림을 전송합니다."
            )
            
            return jsonify({'success': True, 'message': '디스코드 웹훅 URL이 업데이트되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '웹훅 URL 업데이트에 실패했습니다.'})
            
    except Exception as e:
        logging.error(f"Update Discord webhook error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/webhook/secret', methods=['POST'])
def update_webhook_secret():
    """웹훅 시크릿 업데이트"""
    try:
        data = request.json
        secret = data.get('secret', '').strip()
        
        success = config_manager.update_webhook_secret(secret)
        
        if success:
            return jsonify({'success': True, 'message': '웹훅 시크릿이 업데이트되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '웹훅 시크릿 업데이트에 실패했습니다.'})
            
    except Exception as e:
        logging.error(f"Update webhook secret error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """트레이딩뷰 웹훅 수신"""
    try:
        # 헤더에서 시그니처 확인 (보안)
        webhook_secret = config_manager.get_webhook_secret()
        if webhook_secret:
            signature = request.headers.get('X-Webhook-Signature', '')
            if not verify_webhook_signature(request.data, signature, webhook_secret):
                logging.warning("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 401
        
        # JSON 데이터 파싱
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        logging.info(f"Received TradingView webhook: {json.dumps(data, indent=2)}")
        
        # 트레이딩 시그널 처리
        result = trading_engine.process_tradingview_signal(data)
        
        if result.get('success'):
            return jsonify({
                'status': 'success',
                'message': 'Signal processed successfully',
                'order_id': result.get('order_id')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Unknown error')
            }), 400
            
    except Exception as e:
        error_msg = f"Webhook processing error: {str(e)}"
        logging.error(error_msg)
        discord_webhook.send_error_alert("Webhook Error", error_msg, str(request.data))
        return jsonify({'error': error_msg}), 500

@app.route('/webhook/discord', methods=['POST'])
def discord_command_webhook():
    """디스코드 명령어 웹훅 (선택적)"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        # 디스코드 메시지에서 명령어 파싱
        content = data.get('content', '')
        if content.startswith('!'):
            command = discord_webhook.parse_command(content)
            if command:
                response = discord_webhook.execute_command(command)
                discord_webhook.send_message(response)
                
                # 클라이언트 새로고침이 필요한 명령어들
                if command['type'] in ['add_kis', 'update_kis', 'delete_kis', 'add_exchange', 'update_exchange']:
                    trading_engine.refresh_clients()
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Discord command error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """봇 상태 조회"""
    try:
        status = trading_engine.get_portfolio_status()
        return jsonify(status)
    except Exception as e:
        logging.error(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-discord')
def test_discord():
    """디스코드 연결 테스트"""
    try:
        success = discord_webhook.send_message(
            f"🧪 **디스코드 연결 테스트**\n"
            f"• 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• 메시지: 연결이 정상적으로 작동합니다!"
        )
        
        if success:
            return jsonify({'success': True, 'message': '디스코드 메시지가 성공적으로 전송되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '디스코드 메시지 전송에 실패했습니다.'})
            
    except Exception as e:
        logging.error(f"Discord test error: {e}")
        return jsonify({'success': False, 'error': str(e)})

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
        f"• 서버 포트: {os.getenv('PORT', '8000')}\n"
        f"• 봇 버전: v1.0"
    )
    
    # Flask 앱 실행
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
