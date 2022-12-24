from rest_framework import serializers
from .models import CustomUser, Post


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password',
                  'ip_address', 'country', 'holiday']


class PostSerializer(serializers.ModelSerializer):
    text = serializers.CharField()
    likes = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'text', 'likes']
