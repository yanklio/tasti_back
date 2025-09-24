from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Recipe
from .permissions import IsOwnerOrReadOnly
from .serializers import RecipeSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recipes.

    Permissions:
    - List/Detail: No authentication required
    - Create: Authentication required
    - Update/Delete: Owner only
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        """Set the owner to the current user when creating a recipe."""
        serializer.save(owner=self.request.user)
