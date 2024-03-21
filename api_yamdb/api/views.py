from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import AdminOrReadOnly
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleEditSerializer, TitleViewSerializer)


class CategoryViewSet(CreateListDestroyViewSet):
    """
    Вьюсет для работы с категориями.

    Позволяет создавать, просматривать и удалять категории.

    Attributes:
    - queryset: Запрос для получения всех категорий.
    - serializer_class: Сериализатор для категорий.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    """
    Вьюсет для работы с жанрами.

    Позволяет создавать, просматривать и удалять жанры.

    Attributes:
    - queryset: Запрос для получения всех жанров.
    - serializer_class: Сериализатор для жанров.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с произведениями.

    Позволяет создавать, просматривать, обновлять и удалять произведения.
    Расчет средней оценки произведения производится автоматически.

    Attributes:
    - queryset: Запрос для получения всех произведений.
    - permission_classes: Кортеж классов разрешений.
    - filter_backends: Кортеж фильтров для обработки запросов.
    - filterset_class: Класс фильтров для произведений.
    - http_method_names: Кортеж HTTP методов, поддерживаемых вьюсетом.
    """

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'delete', 'patch')

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от метода запроса.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return TitleViewSerializer
        return TitleEditSerializer
