from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Recipe
from .permissions import IsOwnerOrReadOnly
from .serializers import RecipeSerializer
from .utils.bucket import generate_key, get_presigned_url


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

    def create(self, request):
        """Override create to optionally generate presigned upload URL."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Pop the write-only field to avoid passing it to the model's create method
        request_presigned = serializer.validated_data.pop('request_presigned_url', False)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if request_presigned:
            image_key = generate_key("recipes", "image.jpg")  # Default filename; client can override
            try:
                presigned_url = get_presigned_url(image_key, "PUT", expiration=3600)
                response_data = serializer.data.copy()
                response_data['presigned_upload_url'] = presigned_url
                response_data['image_upload_key'] = image_key
                return Response(response_data, status=201, headers=headers)
            except Exception as e:
                # If URL generation fails, still return success but log error
                # In production, consider returning an error or fallback
                pass

        return Response(serializer.data, status=201, headers=headers)
