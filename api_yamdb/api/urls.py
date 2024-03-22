from django.urls import include, path

from rest_framework.routers import DefaultRouter
from users.views import CreateUserViewSet, ReceiveTokenViewSet, UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')


urlpatterns = [
    path(
        'v1/auth/signup/',
        CreateUserViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        'v1/auth/token/',
        ReceiveTokenViewSet.as_view({'post': 'create'}),
        name='token'
    ),
    path('v1/', include(router_v1.urls)),
]
