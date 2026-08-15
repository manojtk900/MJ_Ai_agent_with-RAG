"""
Task Scheduler Service using APScheduler.
Handles persistent background reminders, one-time scheduled tasks, and cron jobs.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

log = structlog.get_logger(__name__)

class TaskScheduler:
    _instance: Optional[TaskScheduler] = None

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    @classmethod
    def get_instance(cls) -> TaskScheduler:
        if cls._instance is None:
            cls._instance = TaskScheduler()
        return cls._instance

    def start(self) -> None:
        """Start the background scheduler."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            log.info("✅ TaskScheduler (APScheduler) started")

    def shutdown(self) -> None:
        """Shutdown the background scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            log.info("🛑 TaskScheduler stopped")

    def schedule_one_time_reminder(
        self,
        task_id: str,
        title: str,
        run_at: datetime,
        callback_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule a one-time reminder at specific datetime."""
        job_id = f"reminder_{task_id}"

        def trigger_reminder():
            log.info("🔔 REMINDER TRIGGERED", task_id=task_id, title=title, data=callback_data)

        self.scheduler.add_job(
            trigger_reminder,
            trigger=DateTrigger(run_date=run_at),
            id=job_id,
            replace_existing=True,
        )
        log.info("Scheduled one-time reminder", job_id=job_id, run_at=run_at.isoformat(), title=title)
        return job_id

    def schedule_recurring_reminder(
        self,
        task_id: str,
        title: str,
        cron_expression: str,
        callback_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule a recurring reminder with a cron expression."""
        job_id = f"cron_{task_id}"

        def trigger_reminder():
            log.info("🔔 RECURRING REMINDER TRIGGERED", task_id=task_id, title=title, cron=cron_expression)

        try:
            trigger = CronTrigger.from_crontab(cron_expression)
            self.scheduler.add_job(
                trigger_reminder,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
            )
            log.info("Scheduled recurring reminder", job_id=job_id, cron=cron_expression, title=title)
            return job_id
        except Exception as e:
            log.error("Failed to schedule cron job", error=str(e), cron=cron_expression)
            raise

scheduler_service = TaskScheduler.get_instance()
