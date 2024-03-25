from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (decorators, filters, mixins, pagination,
                            permissions, response, status, viewsets)
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


from api_yamdb.settings import EMAIL_ADMIN, ME_URL
from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrModeratorsOrReadOnly)
from .serializers import (AdminUsersSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, LoginSerializer,
                          ReviewSerializer, TitleEditSerializer,
                          TitleViewSerializer, TokenSerializer, UserSerializer)

User = get_user_model()


class CategoryGenreBaseViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """GET, POST и DELETE запросы."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = pagination.LimitOffsetPagination


class CategoryViewSet(CategoryGenreBaseViewSet):
    """
    Вьюсет для работы с категориями.

    Позволяет создавать, просматривать и удалять категории.

    Attributes:
    - queryset: Запрос для получения всех категорий.
    - serializer_class: Сериализатор для категорий.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
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

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by(
        *Title._meta.ordering
    )
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
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    http_method_names = ('get', 'post', 'patch', 'delete')

    @decorators.action(methods=('GET', 'PATCH'),
                       permission_classes=(permissions.IsAuthenticated,),
                       url_path=ME_URL,
                       detail=False,)
    def get_patch_user_info(self, request):
        """
        Получает или обновляет информацию о текущем пользователе.
        """
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
        else:
            serializer = UserSerializer(
                request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["POST"])
def api_sign_up(request):
    """
    Регистрация пользователя.
    Создает нового пользователя на основе предоставленных данных.
    Отправляет код подтверждения на указанный email пользователя.
    Args:
    - request: Объект запроса.
    Returns:
    - response.Response: Объект ответа, содержащий
    данные о регистрации пользователя.

    Raises:
    - ValidationError: Если данные в запросе неверные.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        user, _ = User.objects.get_or_create(
            username=data.get('username'),
            email=data.get('email')
        )
    except IntegrityError:
        raise ValidationError(
            'Пользователь с таким username или email уже существует')
    send_mail(
        'Код для получения токена к API',
        f'Код подтверждения {default_token_generator.make_token(user)}',
        f'{EMAIL_ADMIN}',
        [user.email],
    )
    return response.Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["POST"])
def get_api_token(request):
    """
    Получение API токена.
    Проверяет подтверждающий код пользователя и выдает
    ему API токен для аутентификации.
    Args:
    - request: Объект запроса.
    Returns:
    - response.Response: Объект ответа, содержащий API токен.
    Raises:
    - ValidationError: Если указан неверный код подтверждения.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = get_object_or_404(User, username=data.get('username'))
    if default_token_generator.check_token(
        user, data.get('confirmation_code')
    ):
        api_token = RefreshToken.for_user(user).access_token
        return response.Response(
            {'token': str(api_token)}, status=status.HTTP_200_OK)
    raise ValidationError('Указан неверный код подтверждения')


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
