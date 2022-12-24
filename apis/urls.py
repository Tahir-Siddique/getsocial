from django.urls import path, include
from rest_framework import routers
from .views import PostViewSet, signup, login, get_user

router = routers.DefaultRouter()
router.register('posts', PostViewSet)

urlpatterns = [

    path('', include(router.urls)),
    path('user/signup', signup, name="signup"),
    path('user/login', login, name="login"),
    path('user/get_user', get_user, name="get-user"),
]
