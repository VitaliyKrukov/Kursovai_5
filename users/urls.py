from django.urls import path

from .views import UserProfileView, UserRegistrationView, user_login

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", user_login, name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]
