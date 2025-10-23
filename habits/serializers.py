from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        # Дублируем валидацию из модели для DRF
        is_pleasant = data.get(
            "is_pleasant", self.instance.is_pleasant if self.instance else False
        )
        related_habit = data.get("related_habit")
        reward = data.get("reward")

        # Валидатор 1: Исключить одновременный выбор связанной привычки и указания вознаграждения
        if related_habit and reward:
            raise serializers.ValidationError(
                {
                    "reward": "Нельзя указывать одновременно связанную привычку и вознаграждение.",
                    "related_habit": "Нельзя указывать одновременно связанную привычку и вознаграждение.",
                }
            )

        # Валидатор 2: В связанные привычки могут попадать только привычки с признаком приятной привычки
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                {
                    "related_habit": "В связанные привычки могут попадать только приятные привычки."
                }
            )

        # Валидатор 3: У приятной привычки не может быть вознаграждения или связанной привычки
        if is_pleasant:
            if reward:
                raise serializers.ValidationError(
                    {"reward": "У приятной привычки не может быть вознаграждения."}
                )
            if related_habit:
                raise serializers.ValidationError(
                    {
                        "related_habit": "У приятной привычки не может быть связанной привычки."
                    }
                )

        return data
