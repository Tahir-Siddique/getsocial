import asyncio
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from apis.tasks import enrich_data
from .models import CustomUser, Post
from .serializers import UserSerializer, PostSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .support_functions import validate_email
from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.ViewSet):

    """
    ViewSet for the CustomUser model. Allows users to login, signup, get_user.
    """

    serializer_class = UserSerializer

    def signup(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            try:
                user = serializer.save()
            except IntegrityError:
                return Response({"message": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

            if not validate_email(user.email):
                user.delete()
                return Response({"message": "Email is not real."})
            # user.ip_address = request.META['REMOTE_ADDR']
            user.ip_address = "103.183.244.240"
            user.save()
            enrich_data.delay(user.id)
            token = get_tokens_for_user(user)
            return Response(token, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response(token, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid email or password'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_user(self, request):
        authentication_classes = (JWTAuthentication,)
        permission_classes = (IsAuthenticated,)
        try:
            user = CustomUser.objects.get(pk=request.user.id)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(user)
        return Response(serializer.data)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class PostViewSet(viewsets.ViewSet):
    """
    ViewSet for the Post model. Allows users to create, read, update, and delete their own posts, as well as like and unlike other users' posts.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = self.serializer_class(
            post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(post, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        if post.user != request.user:
            return Response({'message': 'You are not the owner of this post'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(
            post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(post, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        if post.user != request.user:
            return Response({'message': 'You are not the owner of this post'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(
            post, data=request.data, partial=True)
        serializer.delete(post)
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"])
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = self.serializer_class(
            post, data=request.data, partial=True)
        if serializer.is_valid():
            post.likes.add(request.user)
            serializer = self.serializer_class(post)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["put"])
    def unlike(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = self.serializer_class(
            post, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            post.likes.remove(request.user)
            serializer = self.serializer_class(post)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
