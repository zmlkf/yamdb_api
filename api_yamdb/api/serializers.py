from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import BANNED_USERNAME

User = get_user_model()


class AdminUsersSerializer(serializers.ModelSerializer):

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


class UserSerializer(serializers.ModelSerializer):

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
        read_only_fields = ('role',)


class TokenSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if username in BANNED_USERNAME:
            raise serializers.ValidationError(
                f'Имя пользователя не может быть {username}')
        return username


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleViewSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True,)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleEditSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, year):
        if year > timezone.now().year:
            serializers.ValidationError(
                'Год не может быть больше текущего года.')
        return year


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method == 'POST' and Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise serializers.ValidationError('Отзыв уже оставлен')
        return data
