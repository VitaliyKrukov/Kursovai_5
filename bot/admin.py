from django.contrib import admin

from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ["user", "chat_id", "username", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "username", "chat_id"]
    readonly_fields = ["created_at"]
