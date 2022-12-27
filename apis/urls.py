from django.urls import path, include
from rest_framework import routers
from .views import PostViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
# router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('users/signup/',
         UserViewSet.as_view({"post": "signup"}), name='signup'),
    path('users/login/',
         UserViewSet.as_view({"post": "login"}), name='login'),
    path('users/get_user/',
         UserViewSet.as_view({"get": "get_user"}), name='get_user'),
]
