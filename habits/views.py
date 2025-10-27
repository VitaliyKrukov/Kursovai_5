from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Habit
from .permissions import IsOwner
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_pleasant", "is_public"]

    def get_queryset(self):
        if self.action == "public":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == "public":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwner()]

    @action(detail=False, methods=["get"])
    def public(self, request):
        """Список публичных привычек"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
