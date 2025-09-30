from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views_bucket import PresignedUrlView

router = DefaultRouter()
router.register("", views.RecipesViewSet)

urlpatterns = [
    path("presigned-url/", PresignedUrlView.as_view(), name="presigned-url"),
    path("", include(router.urls)),
]

app_name = "recipes"
