from django.urls import path
from .views import CreateUserView


urlpatterns = [
    path('auth/signup/', CreateUserView)
]