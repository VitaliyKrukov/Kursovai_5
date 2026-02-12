from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.models import TelegramUser

User = get_user_model()


class Command(BaseCommand):
    help = "Запуск Telegram бота"

    def handle(self, *args, **options):
        async def main():
            if (
                not settings.TELEGRAM_BOT_TOKEN
                or settings.TELEGRAM_BOT_TOKEN == "your-telegram-bot-token"
            ):
                self.stdout.write(
                    self.style.ERROR("TELEGRAM_BOT_TOKEN не настроен в settings.py")
                )
                return

            application = (
                Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            )

            application.add_handler(CommandHandler("start", start))
            application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            )

            self.stdout.write(self.style.SUCCESS("Бот запущен..."))
            await application.run_polling()

        import asyncio

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Бот остановлен"))


async def start(update, context):
    user = update.effective_user
    chat_id = update.message.chat_id

    try:
        # Ищем пользователя по username в Telegram
        django_user = await sync_to_async(
            User.objects.filter(username=user.username).first
        )()

        if not django_user:
            await update.message.reply_text(
                f"Привет {user.first_name}! Сначала зарегистрируйся на нашем сайте "
                f"с username: {user.username}, затем используй /start снова."
            )
            return

        telegram_user, created = await sync_to_async(
            TelegramUser.objects.update_or_create
        )(user=django_user, defaults={"chat_id": chat_id, "username": user.username})

        if created:
            await update.message.reply_text(
                f"Привет, {user.first_name}! Аккаунт привязан. "
                f"Теперь ты будешь получать уведомления о привычках."
            )
        else:
            await update.message.reply_text(
                f"С возвращением, {user.first_name}! Аккаунт уже привязан."
            )

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def handle_message(update, context):
    await update.message.reply_text("Используй /start для привязки аккаунта.")
