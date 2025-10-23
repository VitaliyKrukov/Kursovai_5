import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from bot.models import TelegramUser

from .models import Habit


@shared_task
def send_telegram_reminder():
    """Отправка напоминаний о привычках через Telegram"""
    now = timezone.now()
    current_time = now.time()

    # Простая логика: проверяем привычки на текущее время ± 1 минута
    habits_to_remind = Habit.objects.filter(
        time__hour=current_time.hour, time__minute=current_time.minute
    )

    bot_token = settings.TELEGRAM_BOT_TOKEN

    for habit in habits_to_remind:
        try:
            telegram_user = TelegramUser.objects.get(user=habit.user)

            message = (
                f"Напоминание о привычке!\n\n"
                f"Я буду {habit.action} в {habit.time.strftime('%H:%M')} в {habit.place}.\n"
                f"Время на выполнение: {habit.duration} секунд.\n"
                f"Периодичность: каждые {habit.periodicity} дней."
            )

            if habit.reward:
                message += f"\nВознаграждение: {habit.reward}"
            elif habit.related_habit:
                message += f"\nСвязанная привычка: {habit.related_habit.action}"

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {"chat_id": telegram_user.chat_id, "text": message}

            response = requests.post(url, data=data)
            response.raise_for_status()

            print(
                f"Отправлено напоминание для привычки {habit.id} пользователю {habit.user}"
            )

        except TelegramUser.DoesNotExist:
            print(f"Пользователь {habit.user} не привязал Telegram")
            continue
        except Exception as e:
            print(f"Ошибка отправки сообщения для привычки {habit.id}: {e}")
            continue
