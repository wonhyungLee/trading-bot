import os
import re
from typing import Dict, Optional, List
from dotenv import load_dotenv, set_key, unset_key
import logging

class ConfigManager:
    def __init__(self, env_file_path: str = ".env"):
        self.env_file_path = env_file_path
        self.load_config()
        
    def load_config(self):
        """환경변수 파일을 로드합니다."""
        load_dotenv(self.env_file_path)
        
    def get_kis_accounts(self) -> List[Dict[str, str]]:
        """모든 KIS 계좌 정보를 가져옵니다."""
        accounts = []
        for i in range(1, 51):  # KIS1 ~ KIS50
            key = os.getenv(f"KIS{i}_KEY", "")
            secret = os.getenv(f"KIS{i}_SECRET", "")
            account_number = os.getenv(f"KIS{i}_ACCOUNT_NUMBER", "")
            account_code = os.getenv(f"KIS{i}_ACCOUNT_CODE", "")
            
            if key or secret or account_number:  # 하나라도 값이 있으면 추가
                accounts.append({
                    "number": i,
                    "key": key,
                    "secret": secret,
                    "account_number": account_number,
                    "account_code": account_code,
                    "active": bool(key and secret and account_number and account_code)
                })
        return accounts
        
    def update_kis_account(self, account_number: int, key: str = None, 
                          secret: str = None, acc_number: str = None, 
                          acc_code: str = None) -> bool:
        """KIS 계좌 정보를 업데이트합니다."""
        try:
            if not (1 <= account_number <= 50):
                raise ValueError("Account number must be between 1 and 50")
                
            prefix = f"KIS{account_number}"
            
            if key is not None:
                set_key(self.env_file_path, f"{prefix}_KEY", key)
            if secret is not None:
                set_key(self.env_file_path, f"{prefix}_SECRET", secret)
            if acc_number is not None:
                set_key(self.env_file_path, f"{prefix}_ACCOUNT_NUMBER", acc_number)
            if acc_code is not None:
                set_key(self.env_file_path, f"{prefix}_ACCOUNT_CODE", acc_code)
                
            self.load_config()
            return True
        except Exception as e:
            logging.error(f"Failed to update KIS account {account_number}: {e}")
            return False
            
    def delete_kis_account(self, account_number: int) -> bool:
        """KIS 계좌 정보를 삭제합니다."""
        try:
            if not (1 <= account_number <= 50):
                raise ValueError("Account number must be between 1 and 50")
                
            prefix = f"KIS{account_number}"
            
            for suffix in ["_KEY", "_SECRET", "_ACCOUNT_NUMBER", "_ACCOUNT_CODE"]:
                try:
                    unset_key(self.env_file_path, f"{prefix}{suffix}")
                except:
                    pass  # 키가 없어도 에러 무시
                    
            self.load_config()
            return True
        except Exception as e:
            logging.error(f"Failed to delete KIS account {account_number}: {e}")
            return False
            
    def get_exchange_config(self, exchange: str) -> Dict[str, str]:
        """거래소 API 설정을 가져옵니다."""
        exchange = exchange.upper()
        
        if exchange == "BINANCE":
            return {
                "key": os.getenv("BINANCE_KEY", ""),
                "secret": os.getenv("BINANCE_SECRET", "")
            }
        elif exchange == "UPBIT":
            return {
                "key": os.getenv("UPBIT_KEY", ""),
                "secret": os.getenv("UPBIT_SECRET", "")
            }
        elif exchange == "BYBIT":
            return {
                "key": os.getenv("BYBIT_KEY", ""),
                "secret": os.getenv("BYBIT_SECRET", "")
            }
        elif exchange == "OKX":
            return {
                "key": os.getenv("OKX_KEY", ""),
                "secret": os.getenv("OKX_SECRET", ""),
                "passphrase": os.getenv("OKX_PASSPHRASE", "")
            }
        elif exchange == "BITGET":
            demo_mode = os.getenv("BITGET_DEMO_MODE", "false").lower() == "true"
            if demo_mode:
                return {
                    "key": os.getenv("BITGET_DEMO_KEY", ""),
                    "secret": os.getenv("BITGET_DEMO_SECRET", ""),
                    "passphrase": os.getenv("BITGET_DEMO_PASSPHRASE", ""),
                    "demo": True
                }
            else:
                return {
                    "key": os.getenv("BITGET_KEY", ""),
                    "secret": os.getenv("BITGET_SECRET", ""),
                    "passphrase": os.getenv("BITGET_PASSPHRASE", ""),
                    "demo": False
                }
        
        return {}
        
    def update_exchange_config(self, exchange: str, **kwargs) -> bool:
        """거래소 API 설정을 업데이트합니다."""
        try:
            exchange = exchange.upper()
            
            if exchange == "BINANCE":
                if "key" in kwargs:
                    set_key(self.env_file_path, "BINANCE_KEY", kwargs["key"])
                if "secret" in kwargs:
                    set_key(self.env_file_path, "BINANCE_SECRET", kwargs["secret"])
                    
            elif exchange == "UPBIT":
                if "key" in kwargs:
                    set_key(self.env_file_path, "UPBIT_KEY", kwargs["key"])
                if "secret" in kwargs:
                    set_key(self.env_file_path, "UPBIT_SECRET", kwargs["secret"])
                    
            elif exchange == "BYBIT":
                if "key" in kwargs:
                    set_key(self.env_file_path, "BYBIT_KEY", kwargs["key"])
                if "secret" in kwargs:
                    set_key(self.env_file_path, "BYBIT_SECRET", kwargs["secret"])
                    
            elif exchange == "OKX":
                if "key" in kwargs:
                    set_key(self.env_file_path, "OKX_KEY", kwargs["key"])
                if "secret" in kwargs:
                    set_key(self.env_file_path, "OKX_SECRET", kwargs["secret"])
                if "passphrase" in kwargs:
                    set_key(self.env_file_path, "OKX_PASSPHRASE", kwargs["passphrase"])
                    
            elif exchange == "BITGET":
                demo_mode = kwargs.get("demo", False)
                prefix = "BITGET_DEMO" if demo_mode else "BITGET"
                
                if "key" in kwargs:
                    set_key(self.env_file_path, f"{prefix}_KEY", kwargs["key"])
                if "secret" in kwargs:
                    set_key(self.env_file_path, f"{prefix}_SECRET", kwargs["secret"])
                if "passphrase" in kwargs:
                    set_key(self.env_file_path, f"{prefix}_PASSPHRASE", kwargs["passphrase"])
                if "demo" in kwargs:
                    set_key(self.env_file_path, "BITGET_DEMO_MODE", str(kwargs["demo"]).lower())
                    
            self.load_config()
            return True
        except Exception as e:
            logging.error(f"Failed to update {exchange} config: {e}")
            return False
            
    def get_discord_webhook_url(self) -> str:
        """디스코드 웹훅 URL을 가져옵니다."""
        return os.getenv("DISCORD_WEBHOOK_URL", "")
        
    def update_discord_webhook_url(self, url: str) -> bool:
        """디스코드 웹훅 URL을 업데이트합니다."""
        try:
            set_key(self.env_file_path, "DISCORD_WEBHOOK_URL", url)
            self.load_config()
            return True
        except Exception as e:
            logging.error(f"Failed to update Discord webhook URL: {e}")
            return False
            
    def get_webhook_secret(self) -> str:
        """트레이딩뷰 웹훅 시크릿을 가져옵니다."""
        return os.getenv("WEBHOOK_SECRET", "")
        
    def update_webhook_secret(self, secret: str) -> bool:
        """트레이딩뷰 웹훅 시크릿을 업데이트합니다."""
        try:
            set_key(self.env_file_path, "WEBHOOK_SECRET", secret)
            self.load_config()
            return True
        except Exception as e:
            logging.error(f"Failed to update webhook secret: {e}")
            return False
