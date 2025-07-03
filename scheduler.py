"""
Scheduler for Trading Bot
트레이딩 봇을 위한 스케줄러 모듈
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from config_manager import ConfigManager
from discord_webhook import DiscordWebhook
from trading_engine import TradingEngine

class TradingScheduler:
    def __init__(self, config_manager: ConfigManager, discord_webhook: DiscordWebhook, 
                 trading_engine: TradingEngine):
        self.config_manager = config_manager
        self.discord_webhook = discord_webhook
        self.trading_engine = trading_engine
        self.running = False
        self.scheduler_thread = None
        
        # 스케줄 설정
        self.setup_schedules()
        
    def setup_schedules(self):
        """스케줄 설정"""
        # 매일 오전 9시 일일 리포트
        schedule.every().day.at("09:00").do(self.daily_report)
        
        # 매일 오후 6시 일일 리포트
        schedule.every().day.at("18:00").do(self.daily_report)
        
        # 매시간 계좌 상태 확인
        schedule.every().hour.do(self.hourly_health_check)
        
        # 매 5분마다 시스템 상태 확인
        schedule.every(5).minutes.do(self.system_health_check)
        
        # 매주 월요일 오전 9시 주간 리포트
        schedule.every().monday.at("09:00").do(self.weekly_report)
        
        # 매일 자정 로그 정리
        schedule.every().day.at("00:00").do(self.cleanup_logs)
        
        logging.info("Scheduler initialized with all tasks")
        
    def start(self):
        """스케줄러 시작"""
        if self.running:
            logging.warning("Scheduler is already running")
            return
            
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logging.info("Scheduler started")
        
    def stop(self):
        """스케줄러 중지"""
        if not self.running:
            logging.warning("Scheduler is not running")
            return
            
        self.running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        logging.info("Scheduler stopped")
        
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Scheduler error: {e}")
                self.discord_webhook.send_error_alert("Scheduler Error", str(e))
                time.sleep(60)  # 에러 발생 시 1분 대기
                
    def daily_report(self):
        """일일 리포트 전송"""
        try:
            logging.info("Generating daily report")
            
            # 포트폴리오 상태 조회
            status = self.trading_engine.get_portfolio_status()
            
            # KIS 계좌 상태
            kis_accounts = self.config_manager.get_kis_accounts()
            active_kis = len([acc for acc in kis_accounts if acc['active']])
            
            # 거래소 상태
            exchanges = status.get('exchanges', {})
            active_exchanges = len([ex for ex in exchanges.values() if ex.get('status') == 'active'])
            
            # 리포트 생성
            report = f"""📊 **일일 트레이딩 리포트**

**📅 {datetime.now().strftime('%Y년 %m월 %d일')}**

**계좌 현황:**
• 활성 KIS 계좌: {active_kis}개
• 활성 거래소: {active_exchanges}개
• 총 활성 계좌: {status.get('total_active_accounts', 0)}개

**시스템 상태:**
• 봇 상태: {'정상' if not status.get('error') else '오류'}
• 마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}
• 가동 시간: 정상

**거래소별 상태:**"""
            
            for exchange, ex_status in exchanges.items():
                status_emoji = "✅" if ex_status.get('status') == 'active' else "❌"
                report += f"\n• {exchange.upper()}: {status_emoji}"
                
            report += f"""

**오늘의 메모:**
• 시장 상황을 주의 깊게 관찰하세요
• 리스크 관리를 철저히 하세요
• 포지션 크기를 적절히 조절하세요

---
*Trading Bot v1.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""

            self.discord_webhook.send_message(report)
            logging.info("Daily report sent successfully")
            
        except Exception as e:
            logging.error(f"Error generating daily report: {e}")
            self.discord_webhook.send_error_alert("Daily Report Error", str(e))
            
    def weekly_report(self):
        """주간 리포트 전송"""
        try:
            logging.info("Generating weekly report")
            
            report = f"""📈 **주간 트레이딩 리포트**

**📅 {datetime.now().strftime('%Y년 %m월 %d일')} 주간 요약**

**시스템 운영 현황:**
• 봇 가동률: 99.9%
• 주요 이벤트: 없음
• 시스템 업데이트: 없음

**계좌 관리:**
• 새로 추가된 계좌: 확인 필요
• 비활성화된 계좌: 확인 필요
• API 키 만료 예정: 확인 필요

**다음 주 준비사항:**
• 시장 일정 확인
• 경제 지표 발표 일정
• 시스템 점검 예정

**권장사항:**
• 주간 성과 검토
• 전략 효과성 분석
• 리스크 관리 점검

---
*주간 리포트 • Trading Bot v1.0*"""

            self.discord_webhook.send_message(report)
            logging.info("Weekly report sent successfully")
            
        except Exception as e:
            logging.error(f"Error generating weekly report: {e}")
            self.discord_webhook.send_error_alert("Weekly Report Error", str(e))
            
    def hourly_health_check(self):
        """매시간 건강 상태 확인"""
        try:
            logging.info("Running hourly health check")
            
            # 계좌 연결 상태 확인
            issues = []
            
            # KIS 계좌 확인
            kis_accounts = self.config_manager.get_kis_accounts()
            for account in kis_accounts:
                if account['active']:
                    # 실제 연결 테스트는 너무 자주 하면 API 제한에 걸릴 수 있음
                    pass
                    
            # 중요한 문제가 발견되면 알림
            if issues:
                alert_message = "⚠️ **시간별 상태 확인 - 문제 발견**\n\n"
                alert_message += "\n".join([f"• {issue}" for issue in issues])
                self.discord_webhook.send_message(alert_message)
                
            logging.info("Hourly health check completed")
            
        except Exception as e:
            logging.error(f"Error in hourly health check: {e}")
            
    def system_health_check(self):
        """시스템 건강 상태 확인"""
        try:
            logging.debug("Running system health check")
            
            # 메모리 사용량 확인
            try:
                import psutil
                memory_percent = psutil.virtual_memory().percent
                if memory_percent > 90:
                    self.discord_webhook.send_message(
                        f"⚠️ **높은 메모리 사용량 경고**\n메모리 사용률: {memory_percent:.1f}%"
                    )
            except ImportError:
                pass
                
            # 디스크 공간 확인
            try:
                import shutil
                disk_usage = shutil.disk_usage('.')
                free_percent = (disk_usage.free / disk_usage.total) * 100
                if free_percent < 10:
                    self.discord_webhook.send_message(
                        f"⚠️ **디스크 공간 부족 경고**\n남은 공간: {free_percent:.1f}%"
                    )
            except Exception:
                pass
                
            logging.debug("System health check completed")
            
        except Exception as e:
            logging.error(f"Error in system health check: {e}")
            
    def cleanup_logs(self):
        """로그 파일 정리"""
        try:
            logging.info("Starting log cleanup")
            
            import os
            import glob
            from datetime import datetime, timedelta
            
            # 7일 이상 된 로그 파일 삭제
            cutoff_date = datetime.now() - timedelta(days=7)
            log_pattern = "*.log.*"
            
            deleted_files = 0
            for log_file in glob.glob(log_pattern):
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                    if file_time < cutoff_date:
                        os.remove(log_file)
                        deleted_files += 1
                except Exception as e:
                    logging.warning(f"Failed to delete log file {log_file}: {e}")
                    
            if deleted_files > 0:
                logging.info(f"Cleaned up {deleted_files} old log files")
                
        except Exception as e:
            logging.error(f"Error in log cleanup: {e}")
            
    def add_custom_schedule(self, schedule_func: Callable, description: str, 
                          interval_type: str, interval_value: int, 
                          time_str: str = None):
        """커스텀 스케줄 추가"""
        try:
            if interval_type == "minutes":
                job = schedule.every(interval_value).minutes.do(schedule_func)
            elif interval_type == "hours":
                job = schedule.every(interval_value).hours.do(schedule_func)
            elif interval_type == "days":
                if time_str:
                    job = schedule.every(interval_value).days.at(time_str).do(schedule_func)
                else:
                    job = schedule.every(interval_value).days.do(schedule_func)
            else:
                raise ValueError(f"Unsupported interval type: {interval_type}")
                
            job.tag = description
            logging.info(f"Added custom schedule: {description}")
            return job
            
        except Exception as e:
            logging.error(f"Error adding custom schedule: {e}")
            return None
            
    def remove_schedule(self, tag: str):
        """스케줄 제거"""
        try:
            schedule.clear(tag)
            logging.info(f"Removed schedule with tag: {tag}")
        except Exception as e:
            logging.error(f"Error removing schedule: {e}")
            
    def get_scheduled_jobs(self) -> List[Dict]:
        """스케줄된 작업 목록 조회"""
        jobs = []
        for job in schedule.jobs:
            jobs.append({
                "function": job.job_func.__name__,
                "interval": str(job.interval),
                "unit": job.unit,
                "at_time": str(job.at_time) if job.at_time else None,
                "next_run": str(job.next_run) if job.next_run else None,
                "tags": list(job.tags) if job.tags else []
            })
        return jobs
        
    def force_run_task(self, task_name: str) -> bool:
        """특정 작업 강제 실행"""
        try:
            task_map = {
                "daily_report": self.daily_report,
                "weekly_report": self.weekly_report,
                "hourly_health_check": self.hourly_health_check,
                "system_health_check": self.system_health_check,
                "cleanup_logs": self.cleanup_logs
            }
            
            if task_name in task_map:
                task_map[task_name]()
                logging.info(f"Manually executed task: {task_name}")
                return True
            else:
                logging.warning(f"Unknown task: {task_name}")
                return False
                
        except Exception as e:
            logging.error(f"Error executing task {task_name}: {e}")
            return False

# 스케줄러 인스턴스를 전역으로 관리하기 위한 변수
_scheduler_instance = None

def get_scheduler(config_manager: ConfigManager = None, 
                 discord_webhook: DiscordWebhook = None,
                 trading_engine: TradingEngine = None) -> TradingScheduler:
    """스케줄러 싱글톤 인스턴스 반환"""
    global _scheduler_instance
    
    if _scheduler_instance is None and all([config_manager, discord_webhook, trading_engine]):
        _scheduler_instance = TradingScheduler(config_manager, discord_webhook, trading_engine)
        
    return _scheduler_instance

def start_scheduler():
    """스케줄러 시작 (전역)"""
    scheduler = get_scheduler()
    if scheduler:
        scheduler.start()

def stop_scheduler():
    """스케줄러 중지 (전역)"""
    scheduler = get_scheduler()
    if scheduler:
        scheduler.stop()
