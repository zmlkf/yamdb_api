from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (decorators, filters, pagination, permissions,
                            response, status, views, viewsets)
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrModeratorsOrReadOnly)
from .serializers import (AdminUsersSerializer, UserSerializer,
                          CategorySerializer, CommentSerializer,
                          GenreSerializer, LoginSerializer, ReviewSerializer,
                          TitleEditSerializer, TitleViewSerializer,
                          TokenSerializer)
from .utils import send_confirmation_code

User = get_user_model()


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
    - pagination_class: Пагинация
    """

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'delete', 'patch')
    pagination_class = pagination.LimitOffsetPagination

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от метода запроса.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return TitleViewSerializer
        return TitleEditSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с пользователями.

    Позволяет создавать, просматривать, обновлять и удалять пользователей.
    Пользователь может получить и изменить свои данные через /users/me/.

    Attributes:
    - queryset: Запрос для получения всех пользователей.
    - serializer_class: Сериализатор для пользователей.
    - permission_classes: Кортеж классов разрешений.
    - lookup_field: Поле для поиска пользователей.
    - filter_backends: Кортеж фильтров для обработки запросов.
    - search_fields: Кортеж полей для поиска пользователей.
    - http_method_names: Кортеж HTTP методов, поддерживаемых вьюсетом.
    """

    queryset = User.objects.all()
    serializer_class = AdminUsersSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    http_method_names = ('get', 'post', 'patch', 'delete')

    @decorators.action(methods=('GET', 'PATCH'),
                       permission_classes=(permissions.IsAuthenticated,),
                       url_path='me',
                       detail=False,)
    def get_patch_user_info(self, request):
        """
        Получает или обновляет информацию о текущем пользователе.
        """
        serializer = AdminUsersSerializer(request.user)
        if request.method != 'PATCH':
            return response.Response(
                serializer.data, status=status.HTTP_200_OK)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от текущего пользователя.
        """
        if self.request.user.is_admin:
            return AdminUsersSerializer
        return UserSerializer


class ApiUserSignup(views.APIView):
    """
    API для получения JWT-токена аутентификации.

    Позволяет пользователям получить JWT-токен через метод POST.

    Methods:
    - post: Обработчик POST запросов для получения JWT-токена.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        # Проверка, существует ли пользователь с таким же именем и почтой
        if User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).exists():
            # Если да, отправить код подтверждения еще раз
            send_confirmation_code(request)
            return response.Response(request.data, status=status.HTTP_200_OK)
        # Если пользователь не существует, продолжить процесс регистрации
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code(request)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class GetApiToken(views.APIView):
    """
    API для получения JWT-токена аутентификации.

    Позволяет пользователям получить JWT-токен через метод POST.

    Methods:
    - post: Обработчик POST запросов для получения JWT-токена.
    """

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data.get('username'))
        # Проверка соответствия переданного кода подтверждения
        # коду подтверждения, отправленному пользователю
        if default_token_generator.check_token(
            user, data.get('confirmation_code')
        ):
            # Создание JWT-токена для пользователя
            api_token = RefreshToken.for_user(user).access_token
            # Возврат ответа с JWT-токеном
            return response.Response({'token': str(api_token)},
                                     status=status.HTTP_200_OK)
        # Возврат сообщения с ошибкой, если код подтверждения неверный
        return response.Response(
            {'confirmation_code': 'Указан неверный код доступа к API.'},
            status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API для работы с отзывами к произведениям.
    Позволяет просматривать, создавать, обновлять и удалять отзывы.

    Methods:
    - get_title(): Получает произведение, к которому относится отзыв.
    - get_queryset(): Получает queryset отзывов для конкретного произведения.
    - perform_create: Создает новый отзыв.

    Attributes:
    - serializer_class: Сериализатор для отзывов.
    - permission_classes: Кортеж классов разрешений для доступа к отзывам.
    - http_method_names: Список разрешенных HTTP методов.
    - pagination_class: Пагинация
    """

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorsOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)
    http_method_names = ('get', 'post', 'delete', 'patch')
    pagination_class = pagination.LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """
    API для работы с комментариями к отзывам.

    Позволяет просматривать, создавать, обновлять и удалять комментарии.

    Methods:
    - get_review(): Получает отзыв, к которому относится комментарий.
    - get_queryset(): Получает queryset комментариев для конкретного отзыва.
    - perform_create(): Создает новый комментарий.

    Attributes:
    - queryset: QuerySet всех комментариев.
    - serializer_class: Сериализатор для комментариев.
    - permission_classes: Кортеж классов разрешений для доступа к комментариям.
    - http_method_names: Список разрешенных HTTP методов.
    """

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorsOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)
    http_method_names = ('get', 'post', 'delete', 'patch')
    pagination_class = pagination.LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
