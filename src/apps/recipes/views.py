from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Recipe
from .permissions import IsOwnerOrReadOnly
from .serializers import RecipeSerializer
from core.utils.bucket import generate_key, get_presigned_url


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

    def perform_destroy(self, instance):
        """Delete the recipe's image from S3 before deleting the recipe."""
        if instance.image_bucket_key:
            try:
                from core.utils.bucket import delete_object
                delete_object(instance.image_bucket_key)
            except Exception:
                # Log error but continue with recipe deletion
                pass
        super().perform_destroy(instance)

    def _generate_upload_url(self, serializer_data, headers, filename="image"):
        """Generate presigned upload URL and return enhanced response."""
        image_key = generate_key("recipes", filename)
        presigned_url = get_presigned_url(image_key, "PUT", expiration=3600)
        
        response_data = serializer_data.copy()
        response_data.update({
            'presigned_upload_url': presigned_url,
            'image_upload_key': image_key
        })
        return Response(response_data, status=201, headers=headers)

    def create(self, request):
        """Override create to optionally generate presigned upload URL."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request_presigned = serializer.validated_data.pop('request_presigned_url', False)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if request_presigned:
            filename = request.data.get('filename', 'image')
            try:
                return self._generate_upload_url(serializer.data, headers, filename)
            except Exception:
                # If URL generation fails, still return success
                pass

        return Response(serializer.data, status=201, headers=headers)

    @action(detail=True, methods=['patch'], permission_classes=[IsOwnerOrReadOnly])
    def update_image(self, request, pk=None):
        """Update or clear the recipe's image based on the provided key."""
        recipe = self.get_object()
        key = request.data.get('image_bucket_key')
        
        if key is None:
            recipe.clear_image()
            return Response({'status': 'image cleared'})
        
        recipe.update_image(key)
        return Response({'status': 'image updated'})

    def _validate_presigned_request(self, method, key):
        """Validate presigned URL request parameters and return normalized key."""
        if not method:
            return Response({"error": "Method is required"}, status=status.HTTP_400_BAD_REQUEST), None

        if method.upper() not in ["GET", "PUT"]:
            return Response(
                {"error": "Method must be GET or PUT"}, status=status.HTTP_400_BAD_REQUEST
            ), None

        # Normalize key
        if not key.startswith("recipes/"):
            key = f"recipes/{key}" if key else "recipes/"

        if key == "recipes/":
            return Response(
                {"error": "Key cannot be empty after prefixing with 'recipes/'"},
                status=status.HTTP_400_BAD_REQUEST,
            ), None

        return None, key  # No validation errors, return normalized key

    def _build_presigned_key(self, key, method, filename):
        """Build the final key for presigned URL generation."""
        if method.upper() == "PUT" and filename:
            key = generate_key(key, filename)
        return key

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def presigned_url(self, request):
        """Generate presigned URLs for S3 operations (GET, PUT)"""
        method = request.data.get("method")
        key = request.data.get("key", "")
        filename = request.data.get("filename")
        expiration = request.data.get("expiration", 3600)

        # Validate request and get normalized key
        validation_error, normalized_key = self._validate_presigned_request(method, key)
        if validation_error:
            return validation_error

        # Build final key
        final_key = self._build_presigned_key(normalized_key, method, filename)

        # Generate presigned URL
        try:
            presigned_url = get_presigned_url(final_key, method, expiration)
            
            return Response({
                "presigned_url": presigned_url,
                "key": final_key,
                "method": method.upper(),
                "expires_in": expiration,
            })

        except Exception as e:
            return Response(
                {"error": f"Error generating presigned URL: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
