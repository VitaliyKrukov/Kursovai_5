from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker

from .models import TelegramUser

User = get_user_model()
fake = Faker()


class TelegramUserModelTest(TestCase):
    """Тесты для модели TelegramUser"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

    def test_create_telegram_user(self):
        """Тест создания Telegram пользователя"""
        telegram_user = TelegramUser.objects.create(
            user=self.user, chat_id="123456789", username="testuser"
        )

        self.assertEqual(telegram_user.user, self.user)
        self.assertEqual(telegram_user.chat_id, "123456789")
        self.assertEqual(telegram_user.username, "testuser")
        self.assertEqual(str(telegram_user), "test@example.com - 123456789")

    def test_telegram_user_unique_chat_id(self):
        """Тест уникальности chat_id"""
        TelegramUser.objects.create(
            user=self.user, chat_id="123456789", username="testuser"
        )

        # Попытка создать второго пользователя с тем же chat_id
        another_user = User.objects.create_user(
            email="another@example.com", username="anotheruser", password="testpass123"
        )

        with self.assertRaises(Exception):  # IntegrityError или другой exception
            TelegramUser.objects.create(
                user=another_user,
                chat_id="123456789",  # Тот же chat_id
                username="anotheruser",
            )

    def test_telegram_user_update_or_create(self):
        """Тест обновления или создания Telegram пользователя"""
        telegram_user, created = TelegramUser.objects.update_or_create(
            user=self.user, defaults={"chat_id": "987654321", "username": "updateduser"}
        )

        self.assertTrue(created)
        self.assertEqual(telegram_user.chat_id, "987654321")

        # Обновление существующего
        telegram_user, created = TelegramUser.objects.update_or_create(
            user=self.user,
            defaults={"chat_id": "111111111", "username": "updatedagain"},
        )

        self.assertFalse(created)
        self.assertEqual(telegram_user.chat_id, "111111111")
