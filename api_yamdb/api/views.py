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
    """GET, POST, and DELETE requests."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = pagination.LimitOffsetPagination


class CategoryViewSet(CategoryGenreBaseViewSet):
    """
    ViewSet for working with categories.

    Allows creating, viewing, and deleting categories.

    Attributes:
    - queryset: Query to retrieve all categories.
    - serializer_class: Serializer for categories.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """
    ViewSet for working with genres.

    Allows creating, viewing, and deleting genres.

    Attributes:
    - queryset: Query to retrieve all genres.
    - serializer_class: Serializer for genres.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for working with titles.

    Allows creating, viewing, updating, and deleting titles.
    Automatically calculates the average rating of titles.

    Attributes:
    - queryset: Query to retrieve all titles.
    - permission_classes: Tuple of permission classes.
    - filter_backends: Tuple of filters to process requests.
    - filterset_class: Filter class for titles.
    - http_method_names: Tuple of HTTP methods supported by the viewset.
    - pagination_class: Pagination.
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
        Determines the serializer class based on the request method.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return TitleViewSerializer
        return TitleEditSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for working with users.

    Allows creating, viewing, updating, and deleting users.
    Users can get and modify their data via /users/me/.

    Attributes:
    - queryset: Query to retrieve all users.
    - serializer_class: Serializer for users.
    - permission_classes: Tuple of permission classes.
    - lookup_field: Field for searching users.
    - filter_backends: Tuple of filters to process requests.
    - search_fields: Tuple of fields for searching users.
    - http_method_names: Tuple of HTTP methods supported by the viewset.
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
        Retrieves or updates information about the current user.
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
    User registration.
    Creates a new user based on the provided data.
    Sends a confirmation code to the user's email.

    Args:
    - request: Request object.

    Returns:
    - response.Response: Response object containing
    user registration data.

    Raises:
    - ValidationError: If the data in the request is invalid.
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
            'A user with this username or email already exists')
    send_mail(
        'Confirmation code to access the API',
        f'Confirmation code: {default_token_generator.make_token(user)}',
        f'{EMAIL_ADMIN}',
        [user.email],
    )
    return response.Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["POST"])
def get_api_token(request):
    """
    Get API token.
    Verifies the user's confirmation code and issues
    an API token for authentication.

    Args:
    - request: Request object.

    Returns:
    - response.Response: Response object containing the API token.

    Raises:
    - ValidationError: If an incorrect confirmation code is specified.
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
    raise ValidationError('Incorrect confirmation code')


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API for working with reviews for titles.
    Allows viewing, creating, updating, and deleting reviews.

    Methods:
    - get_title(): Get the title to which the review belongs.
    - get_queryset(): Get the reviews queryset for a specific title.
    - perform_create: Create a new review.

    Attributes:
    - serializer_class: Serializer for reviews.
    - permission_classes: Tuple of permission classes for accessing reviews.
    - http_method_names: List of allowed HTTP methods.
    - pagination_class: Pagination.
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
    API for working with comments for reviews.

    Allows viewing, creating, updating, and deleting comments.

    Methods:
    - get_review(): Get the review to which the comment belongs.
    - get_queryset(): Get the comments queryset for a specific review.
    - perform_create(): Create a new comment.

    Attributes:
    - queryset: QuerySet of all comments.
    - serializer_class: Serializer for comments.
    - permission_classes: Tuple of permission classes for accessing comments.
    - http_method_names: List of allowed HTTP methods.
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
