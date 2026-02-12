from celery.schedules import crontab

from config.celery import app

app.conf.beat_schedule = {
    "send-habit-reminders": {
        "task": "habits.tasks.send_telegram_reminder",
        "schedule": crontab(minute="*/5"),  # Каждые 5 минут
    },
}
