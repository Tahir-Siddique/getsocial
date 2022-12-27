from rest_framework import serializers
from .models import CustomUser, Post
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()
    password = serializers.CharField()
    country = serializers.CharField(required=False)
    holiday = serializers.CharField(required=False)

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.password = make_password(user.password)
        user.save()
        return user

    class Meta:
        model = CustomUser
        required_fields = ('email', 'password')
        fields = ['id', 'email', 'country', 'holiday']


class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField()
    user = UserSerializer(required=False)
    likes = UserSerializer(many=True, required=False)

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        post.save()
        return post

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()

    class Meta:
        model = Post
        required_fields = ('text')
