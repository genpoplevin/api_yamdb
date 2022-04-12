from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import singup, token_jwt, UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', singup, name='singup'),
    path('v1/auth/token/', token_jwt, name='token')
]
