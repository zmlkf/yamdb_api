from rest_framework import serializers

from .constants import BANNED_USERNAME, MAX_LENGHT_FIELD
from .models import User


class BaseUser(serializers.ModelSerializer):

    def validate_username(self, data):
        if self.initial_data.get('username', '').lower() == BANNED_USERNAME:
            raise serializers.ValidationError(
                f'Имя пользователя {BANNED_USERNAME} запрещено.'
            )
        return data


class UserSerializer(BaseUser):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class CreateUserSerializer(BaseUser):
    class Meta:
        model = User
        fields = ('username', 'email',)


class RecieveTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=MAX_LENGHT_FIELD,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=MAX_LENGHT_FIELD,
        required=True
    )
