from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    TokenSerializer,
    UserSerializer,
)
from .utils.cookies import (
    delete_refresh_token_cookie,
    get_refresh_token_from_request,
    set_refresh_token_cookie,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        token_data = TokenSerializer.get_token_for_user(user)

        response = Response(
            {
                "message": "User registered successfully",
                "access": token_data["access"],
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

        set_refresh_token_cookie(response, token_data["refresh"])

        return response


class LoginView(APIView):
    """User login endpoint."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token_data = TokenSerializer.get_token_for_user(user)

        response = Response(
            {
                "message": "User logged in successfully",
                "access": token_data["access"],
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

        set_refresh_token_cookie(response, token_data["refresh"])

        return response


class LogoutView(APIView):
    """Simple logout endpoint."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK,
        )

        delete_refresh_token_cookie(response)
        return response


class CustomTokenRefreshView(APIView):
    """Custom token refresh view that gets refresh token from httpOnly cookie."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie instead of request body
        refresh_token = get_refresh_token_from_request(request)

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Validate and refresh the token
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)

            # Get user info
            user_id = token.payload.get("user_id")
            user = User.objects.get(id=user_id)

            response = Response(
                {
                    "access": new_access_token,
                    "user": UserSerializer(user).data,
                }
            )

            # Optionally rotate the refresh token for better security
            if getattr(settings, "ROTATE_REFRESH_TOKENS", False):
                new_refresh_token = str(RefreshToken.for_user(user))
                set_refresh_token_cookie(response, new_refresh_token)

            return response

        except (TokenError, InvalidToken, User.DoesNotExist):
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
