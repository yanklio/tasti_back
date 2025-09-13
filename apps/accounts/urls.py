from django.urls import path

from . import views

urlpatterns = [
    # Authentication endpoints
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # Token management
    path(
        "token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
]

app_name = "accounts"
