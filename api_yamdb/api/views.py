from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import viewsets, filters, permissions, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from http.client import OK, BAD_REQUEST
from api.serializers import (SignUpSerializer, TokenSerializer, UserSerializer,
                             CategorySerializer, GenreSerializer,
                             TitleCreateSerializer, TitleReadSerializer,
                             ReviewSerializer, CommentSerializer)
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsAuthorOrAdminOrModeratorOrReadOnly)
from api.filters import TitleFilter
from reviews.models import User, Category, Genre, Title, Comment, Review


class HTTPMethod:
    GET = 'get'
    PATCH = 'patch'
    DELETE = 'delete'
    POST = 'post'


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def singup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="Регистрация на YamDB",
        message=f"Код для токена: {confirmation_code}",
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def token_jwt(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
    if default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=OK)

    return Response(serializer.errors, status=BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', ]
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    @action(detail=False,
            methods=[HTTPMethod.GET, HTTPMethod.PATCH, ],
            permission_classes=[IsAuthenticated, ])
    def me(self, request):
        serializer = UserSerializer(request.user,
                                    data=request.data,
                                    partial=True)
        if request.user.is_admin or request.user.is_moderator:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=OK)
        serializer.is_valid(raise_exception=True)
        serializer.save(role='user')
        return Response(serializer.data, status=OK)


class ListCreateDestroyMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class CategoryViewSet(ListCreateDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class GenreViewSet(ListCreateDestroyMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleCreateSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly, ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly, ]

    def get_queryset(self):
        id_review = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=id_review)
        return review.comments.all()

    def perform_create(self, serializer):
        id_review = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=id_review)
        serializer.save(author=self.request.user, review=review)
