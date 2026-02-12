from django.conf import settings
from django.db import models


class TelegramUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram"
    )
    chat_id = models.CharField(
        max_length=100, unique=True, verbose_name="Chat ID в Telegram"
    )
    username = models.CharField(
        max_length=100, blank=True, verbose_name="Username в Telegram"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата подключения"
    )

    class Meta:
        verbose_name = "Telegram пользователь"
        verbose_name_plural = "Telegram пользователи"

    def __str__(self):
        return f"{self.user.email} - {self.chat_id}"
