from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Recipe
from .serializers import RecipeSerializer


# Create your views here.
class RecipesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recipes.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]
