from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(
        read_only=True
    )
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            review = Review.objects.filter(
                title=self.context['view'].kwargs.get('title_id'),
                author=self.context['request'].user
            )
            if review.exists():
                raise serializers.ValidationError(
                    'Ваш отзыв на это произведение уже опубликован'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
