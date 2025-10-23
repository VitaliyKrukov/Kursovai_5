from django.contrib.auth import authenticate, get_user_model, login
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def user_login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, username=email, password=password)

    if user is not None:
        login(request, user)
        return Response({"message": "Успешный вход", "user": UserSerializer(user).data})
    else:
        return Response(
            {"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
