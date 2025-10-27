from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()
fake = Faker()


class UserModelTest(TestCase):
    """Тесты для модели User"""

    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(str(user), "test@example.com")

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="adminpass123"
        )

        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class UserSerializerTest(TestCase):
    """Тесты для сериализаторов пользователей"""

    def test_user_registration_serializer_valid(self):
        """Тест валидных данных регистрации"""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_user_registration_serializer_invalid_password(self):
        """Тест невалидных паролей при регистрации"""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "differentpass",  # Пароли не совпадают
            "first_name": "John",
            "last_name": "Doe",
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_user_serializer(self):
        """Тест сериализатора пользователя"""
        user = User.objects.create_user(
            email="serializer@example.com",
            username="serializeruser",
            password="testpass123",
        )

        serializer = UserSerializer(user)
        self.assertEqual(serializer.data["email"], "serializer@example.com")


class UserAPITest(APITestCase):
    """Тесты для API эндпоинтов пользователей"""

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        """Тест регистрации пользователя через API"""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_user_profile_authenticated(self):
        """Тест получения профиля аутентифицированным пользователем"""
        user = User.objects.create_user(
            email="profile@example.com",
            password="profilepass123",
            username="profileuser",
        )

        self.client.force_authenticate(user=user)
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "profile@example.com")

    def test_user_profile_unauthenticated(self):
        """Тест получения профиля без аутентификации"""
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
