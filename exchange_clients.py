import ccxt
import requests
import json
import hmac
import hashlib
import base64
import time
from datetime import datetime
from typing import Dict, Optional, List, Any
import logging
from config_manager import ConfigManager

class ExchangeClients:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.clients = {}
        self._initialize_clients()
        
    def _initialize_clients(self):
        """거래소 클라이언트들을 초기화합니다."""
        self._init_binance()
        self._init_upbit()
        self._init_bybit()
        self._init_okx()
        self._init_bitget()
        
    def _init_binance(self):
        """바이낸스 클라이언트 초기화"""
        try:
            config = self.config_manager.get_exchange_config("binance")
            if config.get("key") and config.get("secret"):
                self.clients["binance"] = ccxt.binance({
                    'apiKey': config["key"],
                    'secret': config["secret"],
                    'sandbox': False,
                    'enableRateLimit': True,
                })
                logging.info("Binance client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Binance client: {e}")
            
    def _init_upbit(self):
        """업비트 클라이언트 초기화"""
        try:
            config = self.config_manager.get_exchange_config("upbit")
            if config.get("key") and config.get("secret"):
                # 업비트는 CCXT로 직접 지원하지 않으므로 커스텀 클라이언트 사용
                self.clients["upbit"] = UpbitClient(config["key"], config["secret"])
                logging.info("Upbit client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Upbit client: {e}")
            
    def _init_bybit(self):
        """바이비트 클라이언트 초기화"""
        try:
            config = self.config_manager.get_exchange_config("bybit")
            if config.get("key") and config.get("secret"):
                self.clients["bybit"] = ccxt.bybit({
                    'apiKey': config["key"],
                    'secret': config["secret"],
                    'sandbox': False,
                    'enableRateLimit': True,
                })
                logging.info("Bybit client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Bybit client: {e}")
            
    def _init_okx(self):
        """OKX 클라이언트 초기화"""
        try:
            config = self.config_manager.get_exchange_config("okx")
            if config.get("key") and config.get("secret") and config.get("passphrase"):
                self.clients["okx"] = ccxt.okx({
                    'apiKey': config["key"],
                    'secret': config["secret"],
                    'password': config["passphrase"],
                    'sandbox': False,
                    'enableRateLimit': True,
                })
                logging.info("OKX client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize OKX client: {e}")
            
    def _init_bitget(self):
        """비트겟 클라이언트 초기화"""
        try:
            config = self.config_manager.get_exchange_config("bitget")
            if config.get("key") and config.get("secret") and config.get("passphrase"):
                self.clients["bitget"] = ccxt.bitget({
                    'apiKey': config["key"],
                    'secret': config["secret"],
                    'password': config["passphrase"],
                    'sandbox': config.get("demo", False),
                    'enableRateLimit': True,
                })
                logging.info("Bitget client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Bitget client: {e}")
            
    def get_client(self, exchange: str):
        """거래소 클라이언트를 가져옵니다."""
        return self.clients.get(exchange.lower())
        
    def get_balance(self, exchange: str) -> Optional[Dict]:
        """잔고를 조회합니다."""
        try:
            client = self.get_client(exchange)
            if not client:
                return None
                
            if exchange.lower() == "upbit":
                return client.get_balance()
            else:
                return client.fetch_balance()
        except Exception as e:
            logging.error(f"Failed to get balance from {exchange}: {e}")
            return None
            
    def create_order(self, exchange: str, symbol: str, side: str, 
                    amount: float, price: float = None, order_type: str = "market") -> Optional[Dict]:
        """주문을 생성합니다."""
        try:
            client = self.get_client(exchange)
            if not client:
                return None
                
            if exchange.lower() == "upbit":
                return client.create_order(symbol, side, amount, price, order_type)
            else:
                return client.create_order(symbol, order_type, side, amount, price)
        except Exception as e:
            logging.error(f"Failed to create order on {exchange}: {e}")
            return None
            
    def get_ticker(self, exchange: str, symbol: str) -> Optional[Dict]:
        """티커 정보를 가져옵니다."""
        try:
            client = self.get_client(exchange)
            if not client:
                return None
                
            if exchange.lower() == "upbit":
                return client.get_ticker(symbol)
            else:
                return client.fetch_ticker(symbol)
        except Exception as e:
            logging.error(f"Failed to get ticker from {exchange}: {e}")
            return None
            
    def refresh_clients(self):
        """클라이언트들을 새로고침합니다."""
        self.clients.clear()
        self._initialize_clients()


class UpbitClient:
    """업비트 전용 클라이언트"""
    
    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://api.upbit.com"
        
    def _generate_signature(self, query_string: str = "") -> str:
        """JWT 토큰을 생성합니다."""
        import jwt
        
        payload = {
            'access_key': self.access_key,
            'nonce': str(int(time.time() * 1000)),
        }
        
        if query_string:
            payload['query_hash'] = hashlib.sha512(query_string.encode()).hexdigest()
            payload['query_hash_alg'] = 'SHA512'
            
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
        
    def _request(self, method: str, endpoint: str, params: Dict = None) -> Dict:
        """API 요청을 보냅니다."""
        url = f"{self.base_url}{endpoint}"
        
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        else:
            query_string = ""
            
        headers = {
            'Authorization': f'Bearer {self._generate_signature(query_string)}',
            'Content-Type': 'application/json'
        }
        
        if method.upper() == "GET":
            response = requests.get(url, params=params, headers=headers)
        else:
            response = requests.post(url, json=params, headers=headers)
            
        return response.json()
        
    def get_balance(self) -> Dict:
        """잔고를 조회합니다."""
        return self._request("GET", "/v1/accounts")
        
    def get_ticker(self, symbol: str) -> Dict:
        """티커 정보를 가져옵니다."""
        params = {"markets": symbol}
        return self._request("GET", "/v1/ticker", params)
        
    def create_order(self, symbol: str, side: str, amount: float, 
                    price: float = None, order_type: str = "market") -> Dict:
        """주문을 생성합니다."""
        params = {
            "market": symbol,
            "side": side,
            "ord_type": order_type,
        }
        
        if order_type == "limit":
            params["price"] = str(price)
            params["volume"] = str(amount)
        else:  # market order
            if side == "bid":  # 매수
                params["price"] = str(amount)  # 매수는 총 가격
            else:  # 매도
                params["volume"] = str(amount)  # 매도는 수량
                
        return self._request("POST", "/v1/orders", params)


class KISClient:
    """한국투자증권 API 클라이언트"""
    
    def __init__(self, app_key: str, app_secret: str, account_number: str, account_code: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.account_number = account_number
        self.account_code = account_code
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = None
        self._get_access_token()
        
    def _get_access_token(self):
        """액세스 토큰을 발급받습니다."""
        try:
            url = f"{self.base_url}/oauth2/tokenP"
            data = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get("access_token"):
                self.access_token = result["access_token"]
                logging.info("KIS access token obtained")
            else:
                logging.error(f"Failed to get KIS access token: {result}")
        except Exception as e:
            logging.error(f"Error getting KIS access token: {e}")
            
    def _request(self, method: str, endpoint: str, tr_id: str, data: Dict = None) -> Dict:
        """API 요청을 보냅니다."""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id,
        }
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data)
        else:
            headers["custtype"] = "P"  # 개인
            response = requests.post(url, headers=headers, json=data)
            
        return response.json()
        
    def get_balance(self) -> Dict:
        """잔고를 조회합니다."""
        data = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_code,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        return self._request("GET", "/uapi/domestic-stock/v1/trading/inquire-balance", "VTTC8434R", data)
        
    def create_order(self, symbol: str, side: str, quantity: int, price: int = 0, order_type: str = "01") -> Dict:
        """주식 주문을 생성합니다."""
        data = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_code,
            "PDNO": symbol,
            "ORD_DVSN": order_type,  # "01": 지정가, "01": 시장가
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price) if price > 0 else "0",
        }
        
        if side.lower() == "buy":
            tr_id = "VTTC0802U"  # 주식 현금 매수 주문
        else:
            tr_id = "VTTC0801U"  # 주식 현금 매도 주문
            
        return self._request("POST", "/uapi/domestic-stock/v1/trading/order-cash", tr_id, data)
        
    def get_current_price(self, symbol: str) -> Dict:
        """현재가를 조회합니다."""
        data = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
        }
        
        return self._request("GET", "/uapi/domestic-stock/v1/quotations/inquire-price", "FHKST01010100", data)
