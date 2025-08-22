from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

urlpatterns = [
    # Health check endpoints
    path("health/", views.health_check, name="health_check"),
    path("", include(router.urls)),
]

app_name = "core"
