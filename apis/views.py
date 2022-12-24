import asyncio
from rest_framework import viewsets, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from apis.tasks import enrich_data
from .models import CustomUser, Post
from .serializers import UserSerializer, PostSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, authentication_classes
from .support_functions import validate_email


@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():

        user = serializer.save()
        if not validate_email(user.email):
            user.delete()
            return Response({"message": "Email is not real."})
        print(user.password)
        user.password = make_password(user.password)

        user.ip_address = "103.183.244.240"
        # enrich_user(user, request.META['REMOTE_ADDR'])

        user.save()

        enrich_data.delay(user.id)
        # enrich_user(user, "103.183.244.240")
        print("code executed")
        # Generate a JWT token for the user
        token = get_tokens_for_user(user)

        # Return a response with the new user's data and JWT token
        return Response(token, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Generate a JWT token for the user
            token = get_tokens_for_user(user)

            # Return a response with the user's data and JWT token
            return Response(token, status=status.HTTP_200_OK)
    except:
        pass
    return Response({'message': 'Invalid email or password'})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    try:
        user = CustomUser.objects.get(pk=request.user.id)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Post model. Allows users to create, read, update, and delete their own posts, as well as like and unlike other users' posts.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, pk=None):
        post = self.get_object()
        if post.user != request.user:
            return Response({'message': 'You are not the owner of this post'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, pk)

    def destroy(self, request, pk=None):
        post = self.get_object()
        if post.user != request.user:
            return Response({'message': 'You are not the owner of this post'},
                            status=status.HTTP_403_FORBIDDEN)
        super().destroy(request, pk)
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes.add(request.user)
        return Response(PostSerializer(post).data)

    @action(detail=True, methods=["put"])
    def unlike(self, request, pk=None):
        post = self.get_object()
        post.likes.remove(request.user)
        return Response(PostSerializer(post).data)
