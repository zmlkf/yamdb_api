from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import YAMDB_EMAIL
from .models import User
from .permissions import IsSuperUserOrIsAdmin
from .serializers import (
    CreateUserSerializer,
    RecieveTokenSerializer,
    UserSerializer
)


class CreateUserViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = CreateUserSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ):
            user = User.objects.get(username=request.data.get('username'))
            serializer = CreateUserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(username=request.data.get('username'))
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=YAMDB_EMAIL,
            recipient_list=(user.email,),
            fail_silently=False
        )
        return Response(serializer.data, status=HTTP_200_OK)


class ReceiveTokenViewSet(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RecieveTokenSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Неверный код подтверждения'}
            return Response(message, status=HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=HTTP_200_OK)


class UserViewSet(ListModelMixin,
                  CreateModelMixin,
                  UpdateModelMixin,
                  DestroyModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrIsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, *args, **kwargs):
        raise MethodNotAllowed('POST', detail='Use PATCH')

    def partial_update(self, *args, **kwargs):
        return super().update(*args, **kwargs, partial=True)

    @action(
        detail=False,
        methods=('get', 'patch'),
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,),
    )
    def get_me_data(self, request):
        if request.method == 'PATCH':
            serializer = self.serializer_class(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=HTTP_200_OK)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=HTTP_200_OK)
