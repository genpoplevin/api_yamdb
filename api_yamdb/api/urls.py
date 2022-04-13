from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import singup, token_jwt, UserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', singup, name='singup'),
    path('v1/auth/token/', token_jwt, name='token')
]
