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
        """Delete the recipe and its image from S3."""
        # Store the key before deletion
        image_key = instance.image_bucket_key
        
        # Delete the recipe first
        super().perform_destroy(instance)
        
        # If recipe deletion succeeded and there was an image, delete it
        if image_key:
            try:
                from core.utils.bucket import delete_object
                delete_object(image_key)
            except Exception:
                # Log error but don't fail since recipe is already deleted
                pass

    def _generate_upload_url(self, filename="image"):
        """Generate presigned upload URL data."""
        image_key = generate_key("recipes", filename)
        presigned_url = get_presigned_url(image_key, "PUT", expiration=3600)
        
        return {
            'presigned_upload_url': presigned_url,
            'image_upload_key': image_key
        }

    def create(self, request):
        """Override create to optionally generate presigned upload URL."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request_presigned = serializer.validated_data.pop('request_presigned_url', False)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = serializer.data.copy()
        
        if request_presigned:
            filename = request.data.get('filename', 'image')
            try:
                url_data = self._generate_upload_url(filename)
                response_data.update(url_data)
            except Exception:
                response_data['presigned_url_error'] = 'Failed to generate upload URL, but recipe was created successfully'

        return Response(response_data, status=201, headers=headers)

    @action(detail=True, methods=['patch'], permission_classes=[IsOwnerOrReadOnly])
    def update_image(self, request, pk=None):
        """Update or clear the recipe's image based on the provided key."""
        recipe = self.get_object()
        key = request.data.get('image_bucket_key')
        
        # Clear image if key is None, empty, or whitespace-only
        if key is None or str(key).strip() == "":
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
            key = f"recipes/{key}" if key else "recipes"

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
        filename = request.data.get("filename")
        expiration = request.data.get("expiration", 3600)
        
        print("Presigned URL request data:", request.data)

        # Validate request and get normalized key
        validation_error, normalized_key = self._validate_presigned_request(method, '')
        if validation_error:
            return validation_error

        final_key = self._build_presigned_key(normalized_key, method, filename)

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
