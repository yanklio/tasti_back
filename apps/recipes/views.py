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
        print(f"Request user: {self.request.user}")
        print(f"User type: {type(self.request.user)}")
        print(f"Is authenticated: {self.request.user.is_authenticated}")
        print(
            f"User is anonymous: {getattr(self.request.user, 'is_anonymous', 'No attribute')}"
        )

        serializer.save(owner=self.request.user)
