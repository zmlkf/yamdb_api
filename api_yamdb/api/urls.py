from django.urls import include, path
from rest_framework import routers

from api.views import (ApiUserSignup, CategoryViewSet, CommentViewSet,
                       GenreViewSet, GetApiToken, ReviewViewSet, TitleViewSet,
                       UserViewSet)

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

urlpatterns = [
    path('v1/auth/token/', GetApiToken.as_view(), name='get_token'),
    path('v1/auth/signup/', ApiUserSignup.as_view(), name='signup'),
    path('v1/', include(router_v1.urls)),
]
