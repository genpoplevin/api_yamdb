from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]
    username = models.SlugField(
        'Имя пользователя',
        help_text='Имя пользователя',
        max_length=150,
        blank=False,
        unique=True
    )
    email = models.EmailField(
        'Электронная почта',
        help_text='Электронная почта пользователя',
        blank=False,
        unique=True
    )
    bio = models.TextField(
        'Немного о себе',
        help_text='Биография пользователя',
        blank=True,
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        help_text='Код подтверждения пользователя',
        max_length=200,
    )
    role = models.CharField(
        'Роль',
        help_text='Роль пользователя',
        max_length=150,
        blank=False,
        choices=USER_ROLES,
        default='user',
    )

    @property
    def is_admin(self):
        if self.role == self.ADMIN or self.is_superuser:
            return True

    @property
    def is_moderator(self):
        if self.role == self.MODERATOR or self.is_superuser:
            return True

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(
        'название',
        max_length=256,
        default=None
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        'название',
        max_length=100,
        default=None
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=200,
    )
    year = models.IntegerField(
        'год',
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='title_author_unique_together'
            )
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
