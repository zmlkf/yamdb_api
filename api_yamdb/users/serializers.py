from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['email', 'username']
            ),
        ]
