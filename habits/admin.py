from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "action",
        "place",
        "time",
        "is_pleasant",
        "is_public",
        "created_at",
    ]
    list_filter = ["is_pleasant", "is_public", "periodicity", "created_at"]
    search_fields = ["action", "place", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("user", "place", "time", "action", "duration")},
        ),
        ("Тип привычки", {"fields": ("is_pleasant", "is_public", "periodicity")}),
        (
            "Вознаграждения",
            {
                "fields": ("related_habit", "reward"),
                "description": "Можно указать только одно: связанную привычку ИЛИ вознаграждение",
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
