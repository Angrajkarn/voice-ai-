# Celery configuration for background tasks

from app.core.config import settings
from celery import Celery

celery_app = Celery(
    "voiceai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.call_tasks",
        "app.tasks.callback_tasks",
        "app.tasks.sync_tasks",
        "app.tasks.analytics_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_TIME_LIMIT - 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    beat_schedule={
        "process-due-callbacks": {
            "task": "app.tasks.callback_tasks.process_due_callbacks",
            "schedule": 60.0,  # Every minute
        },
        "send-callback-reminders": {
            "task": "app.tasks.callback_tasks.send_callback_reminders",
            "schedule": 300.0,  # Every 5 minutes
        },
        "process-outbound-call-queue": {
            "task": "app.tasks.call_tasks.process_call_queue",
            "schedule": 15.0,
        },
        "retry-failed-calls": {
            "task": "app.tasks.call_tasks.retry_failed_calls",
            "schedule": 3600.0,  # Every hour
        },
        "sync-google-sheets": {
            "task": "app.tasks.sync_tasks.sync_all_campaigns",
            "schedule": 300.0,  # Every 5 minutes
        },
        "update-analytics": {
            "task": "app.tasks.analytics_tasks.update_daily_analytics",
            "schedule": 3600.0,  # Every hour
        },
        "cleanup-old-data": {
            "task": "app.tasks.maintenance_tasks.cleanup_old_data",
            "schedule": 86400.0,  # Daily
        },
    },
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.call_tasks.*": {"queue": "calls"},
    "app.tasks.callback_tasks.*": {"queue": "callbacks"},
    "app.tasks.sync_tasks.*": {"queue": "sync"},
    "app.tasks.analytics_tasks.*": {"queue": "analytics"},
    "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
}

# Worker configuration
celery_app.conf.worker_concurrency = 4
celery_app.conf.worker_prefetch_multiplier = 1