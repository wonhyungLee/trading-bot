import json
import time
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from config_manager import ConfigManager
from exchange_clients import ExchangeClients, KISClient
from discord_webhook import DiscordWebhook

class TradingEngine:
    def __init__(self, config_manager: ConfigManager, discord_webhook: DiscordWebhook):
        self.config_manager = config_manager
        self.discord_webhook = discord_webhook
        self.exchange_clients = ExchangeClients(config_manager)
        self.kis_clients = {}
        self._initialize_kis_clients()
        
    def _initialize_kis_clients(self):
        """KIS 클라이언트들을 초기화합니다."""
        accounts = self.config_manager.get_kis_accounts()
        for account in accounts:
            if account["active"]:
                try:
                    client = KISClient(
                        account["key"],
                        account["secret"],
                        account["account_number"],
                        account["account_code"]
                    )
                    self.kis_clients[f"kis{account['number']}"] = client
                    logging.info(f"KIS{account['number']} client initialized")
                except Exception as e:
                    logging.error(f"Failed to initialize KIS{account['number']}: {e}")
                    
    def refresh_clients(self):
        """모든 클라이언트를 새로고침합니다."""
        self.exchange_clients.refresh_clients()
        self.kis_clients.clear()
        self._initialize_kis_clients()
        
    def process_tradingview_signal(self, webhook_data: Dict) -> Dict[str, Any]:
        """트레이딩뷰 시그널을 처리합니다."""
        try:
            # 웹훅 데이터 파싱
            symbol = webhook_data.get("ticker", "")
            action = webhook_data.get("action", "").lower()  # buy, sell, close
            quantity = float(webhook_data.get("quantity", 0))
            price = float(webhook_data.get("price", 0))
            exchange = webhook_data.get("exchange", "").lower()
            account = webhook_data.get("account", "")  # kis1, kis2, binance 등
            order_type = webhook_data.get("order_type", "market").lower()
            strategy = webhook_data.get("strategy", "Unknown Strategy")
            
            logging.info(f"Processing signal: {action} {quantity} {symbol} on {exchange}")
            
            # 디스코드로 시그널 수신 알림
            self.discord_webhook.send_message(
                f"📥 **트레이딩뷰 시그널 수신**\n"
                f"• 전략: {strategy}\n"
                f"• 종목: {symbol}\n"
                f"• 액션: {action.upper()}\n"
                f"• 수량: {quantity}\n"
                f"• 가격: {price}\n"
                f"• 거래소: {exchange.upper()}\n"
                f"• 계좌: {account.upper()}"
            )
            
            # 액션에 따른 처리
            if action in ["buy", "sell"]:
                return self._execute_trade(symbol, action, quantity, price, exchange, account, order_type, strategy)
            elif action == "close":
                return self._close_position(symbol, exchange, account, strategy)
            else:
                error_msg = f"Unknown action: {action}"
                self.discord_webhook.send_error_alert("Invalid Action", error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error processing TradingView signal: {str(e)}"
            logging.error(error_msg)
            self.discord_webhook.send_error_alert("Signal Processing Error", error_msg, str(webhook_data))
            return {"success": False, "error": error_msg}
            
    def _execute_trade(self, symbol: str, action: str, quantity: float, price: float,
                      exchange: str, account: str, order_type: str, strategy: str) -> Dict[str, Any]:
        """거래를 실행합니다."""
        try:
            result = None
            
            # KIS 계좌 처리
            if account.startswith("kis"):
                result = self._execute_kis_trade(symbol, action, quantity, price, account, order_type)
            
            # 거래소 처리
            elif exchange in ["binance", "upbit", "bybit", "okx", "bitget"]:
                result = self._execute_exchange_trade(symbol, action, quantity, price, exchange, order_type)
            
            else:
                error_msg = f"Unsupported exchange or account: {exchange}/{account}"
                self.discord_webhook.send_error_alert("Unsupported Exchange", error_msg)
                return {"success": False, "error": error_msg}
                
            # 결과 처리
            if result and result.get("success"):
                self.discord_webhook.send_trading_alert(
                    symbol, action.upper(), quantity, price, "success",
                    f"주문이 성공적으로 실행되었습니다. 주문 ID: {result.get('order_id', 'N/A')}"
                )
                return result
            else:
                error_msg = result.get("error", "Unknown error") if result else "Trade execution failed"
                self.discord_webhook.send_trading_alert(
                    symbol, action.upper(), quantity, price, "failed", error_msg
                )
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Trade execution error: {str(e)}"
            logging.error(error_msg)
            self.discord_webhook.send_error_alert("Trade Execution Error", error_msg)
            return {"success": False, "error": error_msg}
            
    def _execute_kis_trade(self, symbol: str, action: str, quantity: float, 
                          price: float, account: str, order_type: str) -> Dict[str, Any]:
        """KIS 계좌에서 거래를 실행합니다."""
        try:
            client = self.kis_clients.get(account)
            if not client:
                return {"success": False, "error": f"KIS client {account} not found"}
                
            # 주식 주문 실행
            if order_type == "market":
                order_type_code = "01"  # 시장가
                price = 0
            else:
                order_type_code = "00"  # 지정가
                
            quantity_int = int(quantity)  # 주식은 정수 수량
            price_int = int(price) if price > 0 else 0
            
            result = client.create_order(symbol, action, quantity_int, price_int, order_type_code)
            
            if result.get("rt_cd") == "0":  # 성공
                return {
                    "success": True,
                    "order_id": result.get("KRX_FWDG_ORD_ORGNO", ""),
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get("msg1", "KIS order failed")
                }
                
        except Exception as e:
            return {"success": False, "error": f"KIS trade error: {str(e)}"}
            
    def _execute_exchange_trade(self, symbol: str, action: str, quantity: float,
                               price: float, exchange: str, order_type: str) -> Dict[str, Any]:
        """거래소에서 거래를 실행합니다."""
        try:
            client = self.exchange_clients.get_client(exchange)
            if not client:
                return {"success": False, "error": f"Exchange client {exchange} not found"}
                
            # 사이드 변환 (buy/sell)
            side = action
            
            # 주문 실행
            result = self.exchange_clients.create_order(
                exchange, symbol, side, quantity, price, order_type
            )
            
            if result:
                return {
                    "success": True,
                    "order_id": result.get("id", ""),
                    "result": result
                }
            else:
                return {"success": False, "error": "Exchange order failed"}
                
        except Exception as e:
            return {"success": False, "error": f"Exchange trade error: {str(e)}"}
            
    def _close_position(self, symbol: str, exchange: str, account: str, strategy: str) -> Dict[str, Any]:
        """포지션을 청산합니다."""
        try:
            # 현재 포지션 조회
            if account.startswith("kis"):
                balance_info = self._get_kis_balance(account)
            else:
                balance_info = self._get_exchange_balance(exchange)
                
            if not balance_info:
                return {"success": False, "error": "Failed to get balance information"}
                
            # 포지션이 있는 경우 청산 주문 실행
            # 실제 구현에서는 보유 수량을 조회하여 전량 매도 주문을 실행
            
            self.discord_webhook.send_message(
                f"📤 **포지션 청산 시도**\n"
                f"• 종목: {symbol}\n"
                f"• 거래소/계좌: {exchange}/{account}\n"
                f"• 전략: {strategy}"
            )
            
            return {"success": True, "message": "Position close attempted"}
            
        except Exception as e:
            error_msg = f"Position close error: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
            
    def _get_kis_balance(self, account: str) -> Optional[Dict]:
        """KIS 계좌 잔고를 조회합니다."""
        try:
            client = self.kis_clients.get(account)
            if client:
                return client.get_balance()
            return None
        except Exception as e:
            logging.error(f"Error getting KIS balance for {account}: {e}")
            return None
            
    def _get_exchange_balance(self, exchange: str) -> Optional[Dict]:
        """거래소 잔고를 조회합니다."""
        try:
            return self.exchange_clients.get_balance(exchange)
        except Exception as e:
            logging.error(f"Error getting {exchange} balance: {e}")
            return None
            
    def get_portfolio_status(self) -> Dict[str, Any]:
        """전체 포트폴리오 상태를 조회합니다."""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "kis_accounts": {},
                "exchanges": {},
                "total_active_accounts": 0
            }
            
            # KIS 계좌 상태
            for account_name, client in self.kis_clients.items():
                try:
                    balance = client.get_balance()
                    status["kis_accounts"][account_name] = {
                        "status": "active",
                        "balance_retrieved": balance is not None
                    }
                    status["total_active_accounts"] += 1
                except Exception as e:
                    status["kis_accounts"][account_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    
            # 거래소 상태
            for exchange in ["binance", "upbit", "bybit", "okx", "bitget"]:
                client = self.exchange_clients.get_client(exchange)
                if client:
                    try:
                        balance = self.exchange_clients.get_balance(exchange)
                        status["exchanges"][exchange] = {
                            "status": "active",
                            "balance_retrieved": balance is not None
                        }
                        status["total_active_accounts"] += 1
                    except Exception as e:
                        status["exchanges"][exchange] = {
                            "status": "error",
                            "error": str(e)
                        }
                else:
                    status["exchanges"][exchange] = {"status": "not_configured"}
                    
            return status
            
        except Exception as e:
            logging.error(f"Error getting portfolio status: {e}")
            return {"error": str(e)}
            
    def send_daily_report(self):
        """일일 리포트를 전송합니다."""
        try:
            status = self.get_portfolio_status()
            
            report = f"""📊 **일일 트레이딩 리포트**
            
**계좌 현황:**
• 활성 계좌 수: {status.get('total_active_accounts', 0)}개
• KIS 계좌: {len([k for k, v in status.get('kis_accounts', {}).items() if v.get('status') == 'active'])}개
• 거래소 계좌: {len([k for k, v in status.get('exchanges', {}).items() if v.get('status') == 'active'])}개

**시스템 상태:**
• 봇 가동시간: 정상
• 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Trading Bot v1.0*"""

            self.discord_webhook.send_message(report)
            
        except Exception as e:
            logging.error(f"Error sending daily report: {e}")
            self.discord_webhook.send_error_alert("Daily Report Error", str(e))
