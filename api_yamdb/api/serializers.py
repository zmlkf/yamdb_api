from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.constants import (MAX_LENGTH_CONFIRMATION_CODE, MAX_LENGTH_EMAIL,
                               MAX_LENGTH_USERNAME)

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import validate_username, validate_year

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


class UserSerializer(AdminUsersSerializer):

    class Meta(AdminUsersSerializer.Meta):
        read_only_fields = 'role',


class TokenSerializer(serializers.Serializer):

    username = serializers.CharField(
        required=True, max_length=MAX_LENGTH_USERNAME)
    confirmation_code = serializers.CharField(
        required=True, max_length=MAX_LENGTH_CONFIRMATION_CODE)

    def validate_username(self, username):
        return validate_username(username)


class LoginSerializer(serializers.Serializer):

    username = serializers.SlugField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        required=True
    )

    def validate_username(self, username):
        return validate_username(username)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleViewSerializer(serializers.ModelSerializer):

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(default=0)

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
        read_only_fields = fields


class TitleEditSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, year):
        return validate_year(year)


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
