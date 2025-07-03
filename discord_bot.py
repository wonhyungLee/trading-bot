import os
import discord
from discord.ext import commands
import asyncio
import json
import logging
from config_manager import ConfigManager
from discord_webhook import DiscordWebhook
from trading_engine import TradingEngine

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 봇 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 컴포넌트 초기화
config_manager = ConfigManager()
discord_webhook = DiscordWebhook(config_manager)
trading_engine = TradingEngine(config_manager, discord_webhook)

@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="Trading Bot v1.0"
    ))

@bot.command(name='add_kis', help='KIS 계좌 추가')
async def add_kis(ctx, number: int, *, args):
    """!add_kis 1 key:YOUR_KEY secret:YOUR_SECRET account:계좌번호 code:상품코드"""
    try:
        # 파라미터 파싱
        params = {}
        for pair in args.split():
            if ':' in pair:
                key, value = pair.split(':', 1)
                params[key] = value
        
        success = config_manager.update_kis_account(
            number, 
            params.get('key'), 
            params.get('secret'), 
            params.get('account'), 
            params.get('code')
        )
        
        if success:
            trading_engine.refresh_clients()
            embed = discord.Embed(
                title="✅ KIS 계좌 추가됨",
                description=f"KIS{number} 계좌가 성공적으로 추가되었습니다.",
                color=discord.Color.green()
            )
            embed.add_field(name="계좌번호", value=params.get('account', 'N/A'), inline=True)
            embed.add_field(name="상품코드", value=params.get('code', 'N/A'), inline=True)
        else:
            embed = discord.Embed(
                title="❌ 추가 실패",
                description=f"KIS{number} 계좌 추가에 실패했습니다.",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")

@bot.command(name='update_kis', help='KIS 계좌 업데이트')
async def update_kis(ctx, number: int, *, args):
    """!update_kis 1 key:NEW_KEY secret:NEW_SECRET"""
    try:
        params = {}
        for pair in args.split():
            if ':' in pair:
                key, value = pair.split(':', 1)
                params[key] = value
        
        success = config_manager.update_kis_account(
            number,
            params.get('key'),
            params.get('secret'),
            params.get('account'),
            params.get('code')
        )
        
        if success:
            trading_engine.refresh_clients()
            embed = discord.Embed(
                title="✅ KIS 계좌 업데이트됨",
                description=f"KIS{number} 계좌가 성공적으로 업데이트되었습니다.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ 업데이트 실패",
                description=f"KIS{number} 계좌 업데이트에 실패했습니다.",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")

@bot.command(name='delete_kis', help='KIS 계좌 삭제')
async def delete_kis(ctx, number: int):
    """!delete_kis 1"""
    try:
        success = config_manager.delete_kis_account(number)
        
        if success:
            trading_engine.refresh_clients()
            embed = discord.Embed(
                title="✅ KIS 계좌 삭제됨",
                description=f"KIS{number} 계좌가 성공적으로 삭제되었습니다.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ 삭제 실패",
                description=f"KIS{number} 계좌 삭제에 실패했습니다.",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")

@bot.command(name='list_kis', help='KIS 계좌 목록 조회')
async def list_kis(ctx):
    """!list_kis"""
    try:
        accounts = config_manager.get_kis_accounts()
        
        if not accounts:
            await ctx.send("📋 등록된 KIS 계좌가 없습니다.")
            return
        
        embed = discord.Embed(
            title="📋 KIS 계좌 목록",
            color=discord.Color.blue()
        )
        
        for acc in accounts:
            status = "✅ 활성" if acc["active"] else "❌ 비활성"
            account_info = f"계좌: {acc['account_number'][:4] + '****' if acc['account_number'] else 'N/A'}\n"
            account_info += f"상품코드: {acc['account_code'] or 'N/A'}"
            
            embed.add_field(
                name=f"KIS{acc['number']} - {status}",
                value=account_info,
                inline=True
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")

@bot.command(name='add_exchange', help='거래소 API 추가')
async def add_exchange(ctx, exchange: str, *, args):
    """!add_exchange binance key:YOUR_KEY secret:YOUR_SECRET"""
    try:
        params = {}
        for pair in args.split():
            if ':' in pair:
                key, value = pair.split(':', 1)
                params[key] = value
        
        success = config_manager.update_exchange_config(
            exchange,
            **params
        )
        
        if success:
            trading_engine.refresh_clients()
            embed = discord.Embed(
                title=f"✅ {exchange.upper()} API 추가됨",
                description=f"{exchange.upper()} API가 성공적으로 추가되었습니다.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ 추가 실패",
                description=f"{exchange.upper()} API 추가에 실패했습니다.",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")

@bot.command(name='status', help='봇 상태 확인')
async def status(ctx):
    """!status"""
    try:
        portfolio_status = trading_engine.get_portfolio_status()
        
        embed = discord.Embed(
            title="📊 Trading Bot 상태",
            color=discord.Color.blue()
        )
        
        # 활성 계좌 수
        embed.add_field(
            name="활성 계좌",
            value=f"{portfolio_status.get('total_active_accounts', 0)}개",
            inline=True
        )
        
        # KIS 계좌 상태
        kis_active = len([k for k, v in portfolio_status.get('kis_accounts', {}).items() 
                         if v.get('status') == 'active'])
        embed.add_field(
            name="KIS 계좌",
            value=f"{kis_active}개 활성",
            inline=True
        )
        
        # 거래소 상태
        exchange_active = len([k for k, v in portfolio_status.get('exchanges', {}).items() 
                             if v.get('status') == 'active'])
        embed.add_field(
            name="거래소",
            value=f"{exchange_active}개 연결됨",
            inline=True
        )
        
        # 타임스탬프
        embed.set_footer(text=f"Last updated: {portfolio_status.get('timestamp', 'N/A')}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")

@bot.command(name='test_webhook', help='트레이딩뷰 웹훅 테스트')
async def test_webhook(ctx):
    """!test_webhook"""
    try:
        webhook_url = f"{os.getenv('BOT_URL', 'http://localhost:8000')}/webhook/tradingview"
        
        embed = discord.Embed(
            title="🧪 웹훅 테스트",
            description="트레이딩뷰 웹훅 URL",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Webhook URL",
            value=f"`{webhook_url}`",
            inline=False
        )
        embed.add_field(
            name="테스트 페이로드 예시",
            value="""```json
{
    "ticker": "AAPL",
    "action": "buy",
    "quantity": 10,
    "price": 150.00,
    "exchange": "nasdaq",
    "account": "kis1",
    "order_type": "market",
    "strategy": "Test Strategy"
}```""",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")

@bot.command(name='help_trading', help='트레이딩봇 도움말')
async def help_trading(ctx):
    """!help_trading"""
    embed = discord.Embed(
        title="🤖 Trading Bot 명령어 도움말",
        description="사용 가능한 명령어 목록",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="**KIS 계좌 관리**",
        value="""
`!add_kis [번호] key:[키] secret:[시크릿] account:[계좌번호] code:[코드]`
`!update_kis [번호] key:[키] secret:[시크릿]`
`!delete_kis [번호]`
`!list_kis`
        """,
        inline=False
    )
    
    embed.add_field(
        name="**거래소 API 관리**",
        value="""
`!add_exchange binance key:[키] secret:[시크릿]`
`!add_exchange upbit key:[키] secret:[시크릿]`
`!add_exchange okx key:[키] secret:[시크릿] passphrase:[패스프레이즈]`
        """,
        inline=False
    )
    
    embed.add_field(
        name="**기타 명령어**",
        value="""
`!status` - 봇 상태 확인
`!test_webhook` - 웹훅 정보 확인
`!help_trading` - 이 도움말
        """,
        inline=False
    )
    
    await ctx.send(embed=embed)

# 봇 실행
if __name__ == '__main__':
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    if bot_token:
        bot.run(bot_token)
    else:
        logging.error("DISCORD_BOT_TOKEN not found in environment variables")
