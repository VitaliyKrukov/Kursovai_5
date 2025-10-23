from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Habit
from .permissions import IsOwner
from .serializers import HabitSerializer
from .tasks import send_telegram_reminder

User = get_user_model()
fake = Faker()


class UserFactory:
    """Фабрика для создания тестовых пользователей"""

    @staticmethod
    def create_user(**kwargs):
        return User.objects.create_user(
            email=kwargs.get("email", fake.email()),
            username=kwargs.get("username", fake.user_name()),
            password=kwargs.get("password", "testpass123"),
            first_name=kwargs.get("first_name", fake.first_name()),
            last_name=kwargs.get("last_name", fake.last_name()),
        )


class HabitFactory:
    """Фабрика для создания тестовых привычек"""

    @staticmethod
    def create_habit(user, **kwargs):
        return Habit.objects.create(
            user=user,
            place=kwargs.get("place", fake.city()),
            time=kwargs.get("time", "08:00:00"),
            action=kwargs.get("action", f"{fake.word()} {fake.word()}"),
            is_pleasant=kwargs.get("is_pleasant", False),
            periodicity=kwargs.get("periodicity", 1),
            reward=kwargs.get("reward", ""),
            related_habit=kwargs.get("related_habit", None),
            duration=kwargs.get("duration", 60),
            is_public=kwargs.get("is_public", False),
        )


class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        self.user = UserFactory.create_user()

    def test_habit_creation(self):
        """Тест создания привычки"""
        habit = HabitFactory.create_habit(
            user=self.user,
            place="Парк",
            time="09:00:00",
            action="гулять",
            is_pleasant=False,
            periodicity=1,
            reward="кофе",
            duration=120,
        )

        self.assertEqual(habit.action, "гулять")
        self.assertEqual(habit.duration, 120)
        self.assertFalse(habit.is_pleasant)
        self.assertEqual(str(habit), "Я буду гулять в 09:00:00 в Парк")

    def test_pleasant_habit_cannot_have_reward(self):
        """Тест: у приятной привычки не может быть вознаграждения"""
        habit = Habit(
            user=self.user,
            place="Дом",
            time="10:00:00",
            action="читать книгу",
            is_pleasant=True,
            reward="не должно быть",
            duration=90,
        )

        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_cannot_have_both_reward_and_related_habit(self):
        """Тест: нельзя указать одновременно вознаграждение и связанную привычку"""
        pleasant_habit = HabitFactory.create_habit(user=self.user, is_pleasant=True)

        habit = Habit(
            user=self.user,
            place="Парк",
            time="11:00:00",
            action="бегать",
            is_pleasant=False,
            related_habit=pleasant_habit,
            reward="и это тоже",
            duration=120,
        )

        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_duration_max_120_seconds(self):
        """Тест: время выполнения не больше 120 секунд"""
        habit = Habit(
            user=self.user,
            place="Парк",
            time="14:00:00",
            action="медитировать",
            is_pleasant=False,
            duration=121,
        )

        with self.assertRaises(ValidationError):
            habit.full_clean()


class HabitSerializerTest(TestCase):
    """Тесты для сериализатора HabitSerializer"""

    def setUp(self):
        self.user = UserFactory.create_user()

    def test_valid_serializer_data(self):
        """Тест валидных данных сериализатора"""
        data = {
            "place": "Парк",
            "time": "08:00:00",
            "action": "бегать",
            "is_pleasant": False,
            "periodicity": 1,
            "reward": "кофе",
            "duration": 120,
        }

        serializer = HabitSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["action"], "бегать")

    def test_serializer_with_invalid_duration(self):
        """Тест сериализатора с невалидной длительностью"""
        data = {
            "place": "Парк",
            "time": "08:00:00",
            "action": "бегать",
            "is_pleasant": False,
            "duration": 121,
        }

        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("duration", serializer.errors)


class IsOwnerPermissionTest(TestCase):
    """Тесты для permission IsOwner"""

    def setUp(self):
        self.owner = UserFactory.create_user()
        self.other_user = UserFactory.create_user()
        self.habit = HabitFactory.create_habit(user=self.owner)
        self.permission = IsOwner()

    def test_has_object_permission_owner(self):
        """Тест разрешения для владельца объекта"""
        request = Mock()
        request.user = self.owner

        result = self.permission.has_object_permission(request, None, self.habit)
        self.assertTrue(result)

    def test_has_object_permission_not_owner(self):
        """Тест запрета для не-владельца объекта"""
        request = Mock()
        request.user = self.other_user

        result = self.permission.has_object_permission(request, None, self.habit)
        self.assertFalse(result)


class HabitAPITest(APITestCase):
    """Тесты для API эндпоинтов привычек"""

    def setUp(self):
        self.user = UserFactory.create_user(
            email="api_test@example.com", username="apitestuser"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_habit(self):
        """Тест создания привычки через API"""
        data = {
            "place": "Офис",
            "time": "09:00:00",
            "action": "работать",
            "is_pleasant": False,
            "periodicity": 1,
            "reward": "перерыв",
            "duration": 120,
        }

        response = self.client.post("/api/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["action"], "работать")

    def test_get_habits_list(self):
        """Тест получения списка привычек"""
        HabitFactory.create_habit(
            user=self.user,
            place="Дом",
            time="08:00:00",
            action="пить кофе",
            is_pleasant=False,
            periodicity=1,
            duration=60,
        )

        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_get_public_habits(self):
        """Тест получения публичных привычек"""
        HabitFactory.create_habit(
            user=self.user,
            place="Библиотека",
            time="10:00:00",
            action="читать",
            is_pleasant=False,
            duration=90,
            is_public=True,
        )

        response = self.client.get("/api/habits/public/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)


class HabitTasksTest(TestCase):
    """Тесты для Celery задач"""

    def setUp(self):
        self.user = UserFactory.create_user()

    @patch("habits.tasks.TelegramUser.objects.get")
    @patch("habits.tasks.requests.post")
    def test_send_telegram_reminder_success(self, mock_post, mock_telegram_get):
        """Тест успешной отправки напоминания"""
        # Настройка моков
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        mock_telegram_user = Mock()
        mock_telegram_user.chat_id = "123456"
        mock_telegram_get.return_value = mock_telegram_user

        # Создаем тестовую привычку
        habit = HabitFactory.create_habit(user=self.user)

        # Вызываем задачу
        with patch("habits.tasks.Habit.objects.filter") as mock_filter:
            mock_filter.return_value = [habit]
            send_telegram_reminder()

        # Проверяем вызовы
        mock_telegram_get.assert_called_once_with(user=self.user)
        mock_post.assert_called_once()
