from django.urls import include, path
from rest_framework import routers

from api.views import (api_sign_up, CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet,
                       UserViewSet, get_api_token)

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('users',
                   UserViewSet,
                   basename='users')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet,
                   basename='review')
router_v1.register((r'titles/(?P<title_id>\d+)/reviews/'
                    r'(?P<review_id>\d+)/comments'),
                   CommentViewSet,
                   basename='comment')
router_v1.register('categories',
                   CategoryViewSet,
                   basename='categories')
router_v1.register('genres',
                   GenreViewSet,
                   basename='genres')
router_v1.register('titles',
                   TitleViewSet,
                   basename='titles')

auth_urls_v1 = [
    path('signup/', api_sign_up, name='signup'),
    path('token/', get_api_token, name='get_token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urls_v1)),
    path('v1/', include(router_v1.urls)),
]
