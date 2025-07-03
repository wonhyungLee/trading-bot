"""
Utility functions for the Trading Bot
트레이딩 봇을 위한 유틸리티 함수들
"""

import os
import json
import time
import hmac
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from decimal import Decimal, ROUND_DOWN
import re

def format_currency(amount: float, currency: str = "USD", decimals: int = 2) -> str:
    """통화 포맷팅"""
    if currency.upper() == "KRW":
        return f"₩{amount:,.0f}"
    elif currency.upper() == "USD":
        return f"${amount:,.{decimals}f}"
    else:
        return f"{amount:,.{decimals}f} {currency.upper()}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """퍼센티지 포맷팅"""
    return f"{value:+.{decimals}f}%"

def truncate_decimal(value: float, decimals: int) -> float:
    """소수점 자리수 자르기 (내림)"""
    multiplier = 10 ** decimals
    return int(value * multiplier) / multiplier

def calculate_position_size(balance: float, risk_percent: float, entry_price: float, 
                          stop_loss_price: float, leverage: float = 1.0) -> float:
    """포지션 크기 계산"""
    if stop_loss_price <= 0 or entry_price <= 0:
        return 0.0
    
    risk_amount = balance * (risk_percent / 100)
    price_diff = abs(entry_price - stop_loss_price)
    risk_per_unit = price_diff / entry_price
    
    if risk_per_unit <= 0:
        return 0.0
    
    position_size = (risk_amount / risk_per_unit) * leverage / entry_price
    return truncate_decimal(position_size, 8)

def validate_symbol(symbol: str, exchange: str) -> bool:
    """심볼 유효성 검증"""
    if not symbol:
        return False
    
    # 기본 패턴 (대부분의 거래소)
    basic_pattern = r'^[A-Z0-9]{2,10}[A-Z]{3,4}$'
    
    # 거래소별 특별 패턴
    exchange_patterns = {
        'upbit': r'^[A-Z]{3,4}-[A-Z0-9]{2,10}$',  # KRW-BTC
        'binance': r'^[A-Z0-9]{2,10}[A-Z]{3,4}$',  # BTCUSDT
        'bybit': r'^[A-Z0-9]{2,10}[A-Z]{3,4}$',    # BTCUSDT
        'okx': r'^[A-Z0-9]{2,10}-[A-Z]{3,4}$',     # BTC-USDT
        'bitget': r'^[A-Z0-9]{2,10}[A-Z]{3,4}_[A-Z]+$',  # BTCUSDT_UMCBL
        'kis': r'^[A-Z0-9]{6}$'  # 종목코드 6자리
    }
    
    pattern = exchange_patterns.get(exchange.lower(), basic_pattern)
    return bool(re.match(pattern, symbol))

def generate_webhook_secret() -> str:
    """웹훅 시크릿 키 생성"""
    return secrets.token_urlsafe(32)

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """웹훅 시그니처 검증"""
    if not signature or not secret:
        return True
    
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # 시그니처 형식 처리
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logging.error(f"Signature verification error: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """파일명 안전화"""
    # 위험한 문자들 제거
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 연속된 언더스코어 제거
    filename = re.sub(r'_{2,}', '_', filename)
    # 앞뒤 공백 및 점 제거
    filename = filename.strip(' .')
    return filename[:255]  # 파일명 길이 제한

def parse_timeframe(timeframe: str) -> int:
    """타임프레임을 초 단위로 변환"""
    timeframe_map = {
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '30m': 1800,
        '1h': 3600,
        '4h': 14400,
        '1d': 86400,
        '1w': 604800
    }
    return timeframe_map.get(timeframe.lower(), 3600)

def get_korean_time() -> datetime:
    """한국 시간 반환"""
    from datetime import timezone, timedelta
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst)

def format_korean_time(dt: datetime = None) -> str:
    """한국 시간 포맷팅"""
    if dt is None:
        dt = get_korean_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S KST')

def mask_api_key(api_key: str) -> str:
    """API 키 마스킹"""
    if not api_key or len(api_key) < 8:
        return "****"
    
    return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

def safe_float(value: Any, default: float = 0.0) -> float:
    """안전한 float 변환"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """안전한 int 변환"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def chunks(lst: List, n: int) -> List[List]:
    """리스트를 n개씩 청크로 나누기"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def retry_on_exception(retries: int = 3, delay: float = 1.0, 
                      exceptions: tuple = (Exception,)):
    """재시도 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries:
                        logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logging.error(f"All {retries + 1} attempts failed")
                        
            raise last_exception
        return wrapper
    return decorator

def calculate_fees(amount: float, fee_rate: float, fee_type: str = "percentage") -> float:
    """수수료 계산"""
    if fee_type == "percentage":
        return amount * (fee_rate / 100)
    elif fee_type == "fixed":
        return fee_rate
    else:
        return 0.0

def get_price_precision(price: float) -> int:
    """가격의 소수점 자릿수 계산"""
    if price >= 1000:
        return 0
    elif price >= 100:
        return 1
    elif price >= 10:
        return 2
    elif price >= 1:
        return 3
    elif price >= 0.1:
        return 4
    elif price >= 0.01:
        return 5
    elif price >= 0.001:
        return 6
    else:
        return 8

def normalize_symbol(symbol: str, from_exchange: str, to_exchange: str) -> str:
    """거래소 간 심볼 정규화"""
    # 심볼 정리
    symbol = symbol.upper().strip()
    
    # 업비트 -> 다른 거래소
    if from_exchange.lower() == 'upbit' and '-' in symbol:
        base, quote = symbol.split('-')
        if to_exchange.lower() in ['binance', 'bybit']:
            return f"{base}{quote}"
        elif to_exchange.lower() == 'okx':
            return f"{base}-{quote}"
        elif to_exchange.lower() == 'bitget':
            return f"{base}{quote}_UMCBL"
    
    # 다른 거래소 -> 업비트
    elif to_exchange.lower() == 'upbit':
        # 일반적인 패턴에서 base/quote 분리
        if from_exchange.lower() in ['binance', 'bybit']:
            # BTCUSDT -> BTC-USDT (업비트는 주로 KRW 쌍)
            if symbol.endswith('USDT'):
                base = symbol[:-4]
                return f"KRW-{base}"
        elif from_exchange.lower() == 'okx' and '-' in symbol:
            base, quote = symbol.split('-')
            return f"KRW-{base}"
    
    return symbol

def create_market_order_message(symbol: str, side: str, quantity: float, 
                               exchange: str, account: str = "") -> Dict:
    """마켓 주문 메시지 생성"""
    return {
        "ticker": symbol,
        "action": side.lower(),
        "quantity": quantity,
        "price": 0,  # 시장가는 가격 0
        "exchange": exchange.lower(),
        "account": account.lower(),
        "order_type": "market",
        "strategy": "Manual Order",
        "timestamp": datetime.now().isoformat()
    }

def create_limit_order_message(symbol: str, side: str, quantity: float, 
                              price: float, exchange: str, account: str = "") -> Dict:
    """지정가 주문 메시지 생성"""
    return {
        "ticker": symbol,
        "action": side.lower(),
        "quantity": quantity,
        "price": price,
        "exchange": exchange.lower(),
        "account": account.lower(),
        "order_type": "limit",
        "strategy": "Manual Order",
        "timestamp": datetime.now().isoformat()
    }

def validate_order_data(order_data: Dict) -> tuple[bool, str]:
    """주문 데이터 유효성 검증"""
    required_fields = ['ticker', 'action', 'quantity']
    
    # 필수 필드 확인
    for field in required_fields:
        if field not in order_data:
            return False, f"Missing required field: {field}"
        
        if not order_data[field]:
            return False, f"Empty required field: {field}"
    
    # 액션 유효성 확인
    valid_actions = ['buy', 'sell', 'close']
    if order_data['action'].lower() not in valid_actions:
        return False, f"Invalid action: {order_data['action']}"
    
    # 수량 유효성 확인
    try:
        quantity = float(order_data['quantity'])
        if quantity <= 0:
            return False, "Quantity must be positive"
    except (ValueError, TypeError):
        return False, "Invalid quantity format"
    
    # 가격 유효성 확인 (지정가인 경우)
    if order_data.get('order_type', 'market').lower() == 'limit':
        try:
            price = float(order_data.get('price', 0))
            if price <= 0:
                return False, "Price must be positive for limit orders"
        except (ValueError, TypeError):
            return False, "Invalid price format"
    
    return True, "Valid"

def load_json_file(filepath: str, default: Any = None) -> Any:
    """JSON 파일 안전 로드"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except Exception as e:
        logging.error(f"Failed to load JSON file {filepath}: {e}")
        return default

def save_json_file(filepath: str, data: Any) -> bool:
    """JSON 파일 안전 저장"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON file {filepath}: {e}")
        return False

def get_memory_usage() -> Dict[str, str]:
    """메모리 사용량 조회"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss": f"{memory_info.rss / 1024 / 1024:.2f} MB",
            "vms": f"{memory_info.vms / 1024 / 1024:.2f} MB",
            "percent": f"{process.memory_percent():.2f}%"
        }
    except ImportError:
        return {"error": "psutil not installed"}
    except Exception as e:
        return {"error": str(e)}

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """RSI 계산"""
    if len(prices) < period + 1:
        return 50.0  # 기본값
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-change)
    
    if len(gains) < period:
        return 50.0
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

# 로깅 유틸리티
class ColoredFormatter(logging.Formatter):
    """컬러 로그 포매터"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # 청록색
        'INFO': '\033[32m',     # 녹색
        'WARNING': '\033[33m',  # 노란색
        'ERROR': '\033[31m',    # 빨간색
        'CRITICAL': '\033[35m', # 자주색
        'RESET': '\033[0m'      # 리셋
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)
