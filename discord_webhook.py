import os
import json
import re
import requests
from datetime import datetime
from typing import Dict, Optional, List
import logging
from config_manager import ConfigManager

class DiscordWebhook:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.webhook_url = config_manager.get_discord_webhook_url()
        
    def send_message(self, content: str, embeds: List[Dict] = None) -> bool:
        """디스코드 채널로 메시지를 전송합니다."""
        if not self.webhook_url:
            logging.warning("Discord webhook URL not configured")
            return False
            
        try:
            payload = {
                "content": content,
                "username": "Trading Bot",
                "avatar_url": "https://cdn.discordapp.com/emojis/1234567890.png"
            }
            
            if embeds:
                payload["embeds"] = embeds
                
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Failed to send Discord message: {e}")
            return False
            
    def send_trading_alert(self, symbol: str, action: str, quantity: float, 
                          price: float, status: str, message: str = "") -> bool:
        """거래 알림을 전송합니다."""
        embed = {
            "title": f"🔄 거래 실행 알림",
            "color": 0x00ff00 if status == "success" else 0xff0000,
            "fields": [
                {"name": "종목", "value": symbol, "inline": True},
                {"name": "액션", "value": action, "inline": True},
                {"name": "수량", "value": str(quantity), "inline": True},
                {"name": "가격", "value": f"${price:,.2f}", "inline": True},
                {"name": "상태", "value": status, "inline": True},
                {"name": "시간", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
            ],
            "footer": {"text": "Trading Bot v1.0"}
        }
        
        if message:
            embed["description"] = message
            
        return self.send_message("", [embed])
        
    def send_error_alert(self, error_type: str, error_message: str, details: str = "") -> bool:
        """에러 알림을 전송합니다."""
        embed = {
            "title": "❌ 에러 발생",
            "color": 0xff0000,
            "fields": [
                {"name": "에러 타입", "value": error_type, "inline": True},
                {"name": "에러 메시지", "value": error_message, "inline": False},
                {"name": "시간", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
            ],
            "footer": {"text": "Trading Bot v1.0"}
        }
        
        if details:
            embed["fields"].append({"name": "상세 정보", "value": details, "inline": False})
            
        return self.send_message("", [embed])
        
    def send_status_update(self, status: str, details: Dict = None) -> bool:
        """상태 업데이트를 전송합니다."""
        embed = {
            "title": "📊 봇 상태 업데이트",
            "color": 0x0099ff,
            "fields": [
                {"name": "상태", "value": status, "inline": True},
                {"name": "시간", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
            ],
            "footer": {"text": "Trading Bot v1.0"}
        }
        
        if details:
            for key, value in details.items():
                embed["fields"].append({"name": key, "value": str(value), "inline": True})
                
        return self.send_message("", [embed])
        
    def parse_command(self, message: str) -> Optional[Dict]:
        """디스코드 메시지에서 명령어를 파싱합니다."""
        if not message.startswith("!"):
            return None
            
        # 명령어 패턴 정의
        patterns = {
            # KIS 계좌 관리
            "add_kis": r"!add_kis (\d+) key:(\S+) secret:(\S+) account:(\S+) code:(\S+)",
            "update_kis": r"!update_kis (\d+) (?:key:(\S+))? ?(?:secret:(\S+))? ?(?:account:(\S+))? ?(?:code:(\S+))?",
            "delete_kis": r"!delete_kis (\d+)",
            "list_kis": r"!list_kis",
            
            # 거래소 API 관리
            "add_exchange": r"!add_(\w+) key:(\S+) secret:(\S+)(?: passphrase:(\S+))?",
            "update_exchange": r"!update_(\w+) (?:key:(\S+))? ?(?:secret:(\S+))? ?(?:passphrase:(\S+))?",
            
            # 디스코드 웹훅 설정
            "set_webhook": r"!set_webhook (\S+)",
            
            # 봇 상태 관리
            "status": r"!status",
            "help": r"!help"
        }
        
        for command_type, pattern in patterns.items():
            match = re.match(pattern, message)
            if match:
                return {
                    "type": command_type,
                    "groups": match.groups()
                }
                
        return {"type": "unknown", "message": message}
        
    def execute_command(self, command: Dict) -> str:
        """명령어를 실행하고 결과를 반환합니다."""
        try:
            cmd_type = command["type"]
            groups = command.get("groups", [])
            
            if cmd_type == "add_kis":
                account_num, key, secret, account, code = groups
                success = self.config_manager.update_kis_account(
                    int(account_num), key, secret, account, code
                )
                return f"✅ KIS{account_num} 계좌가 {'추가' if success else '추가 실패'}되었습니다."
                
            elif cmd_type == "update_kis":
                account_num = int(groups[0])
                key = groups[1] if groups[1] else None
                secret = groups[2] if groups[2] else None
                account = groups[3] if groups[3] else None
                code = groups[4] if groups[4] else None
                
                success = self.config_manager.update_kis_account(
                    account_num, key, secret, account, code
                )
                return f"✅ KIS{account_num} 계좌가 {'업데이트' if success else '업데이트 실패'}되었습니다."
                
            elif cmd_type == "delete_kis":
                account_num = int(groups[0])
                success = self.config_manager.delete_kis_account(account_num)
                return f"✅ KIS{account_num} 계좌가 {'삭제' if success else '삭제 실패'}되었습니다."
                
            elif cmd_type == "list_kis":
                accounts = self.config_manager.get_kis_accounts()
                if not accounts:
                    return "📋 등록된 KIS 계좌가 없습니다."
                    
                result = "📋 **등록된 KIS 계좌 목록:**\n"
                for acc in accounts:
                    status = "✅ 활성" if acc["active"] else "❌ 비활성"
                    result += f"• KIS{acc['number']}: {status}\n"
                return result
                
            elif cmd_type == "add_exchange":
                exchange = groups[0].upper()
                key = groups[1]
                secret = groups[2]
                passphrase = groups[3] if len(groups) > 3 and groups[3] else None
                
                kwargs = {"key": key, "secret": secret}
                if passphrase:
                    kwargs["passphrase"] = passphrase
                    
                success = self.config_manager.update_exchange_config(exchange, **kwargs)
                return f"✅ {exchange} API가 {'추가' if success else '추가 실패'}되었습니다."
                
            elif cmd_type == "set_webhook":
                url = groups[0]
                success = self.config_manager.update_discord_webhook_url(url)
                return f"✅ 디스코드 웹훅 URL이 {'설정' if success else '설정 실패'}되었습니다."
                
            elif cmd_type == "status":
                accounts = self.config_manager.get_kis_accounts()
                active_count = sum(1 for acc in accounts if acc["active"])
                
                return f"""📊 **봇 상태 정보**
• 활성 KIS 계좌: {active_count}개
• 전체 KIS 계좌: {len(accounts)}개
• 서버 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
• 봇 버전: v1.0"""
                
            elif cmd_type == "help":
                return """🤖 **Trading Bot 명령어 도움말**

**KIS 계좌 관리:**
• `!add_kis [번호] key:[키] secret:[시크릿] account:[계좌번호] code:[코드]`
• `!update_kis [번호] key:[키] secret:[시크릿] account:[계좌번호] code:[코드]`
• `!delete_kis [번호]`
• `!list_kis` - 등록된 계좌 목록

**거래소 API 관리:**
• `!add_binance key:[키] secret:[시크릿]`
• `!add_upbit key:[키] secret:[시크릿]`
• `!add_okx key:[키] secret:[시크릿] passphrase:[패스프레이즈]`

**기타:**
• `!set_webhook [URL]` - 웹훅 URL 설정
• `!status` - 봇 상태 확인
• `!help` - 도움말"""
                
            elif cmd_type == "unknown":
                return "❓ 알 수 없는 명령어입니다. `!help`를 입력해 도움말을 확인하세요."
                
        except Exception as e:
            logging.error(f"Command execution error: {e}")
            return f"❌ 명령어 실행 중 오류가 발생했습니다: {str(e)}"
            
        return "❌ 명령어 처리에 실패했습니다."
