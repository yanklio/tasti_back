from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils.bucket import generate_key, get_presigned_url


class PresignedUrlView(APIView):
    """
    Generate presigned URLs for S3 operations (GET, PUT, DELETE)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Generate a presigned URL for file operations in the recipes folder

        Expected payload:
        {
            "method": "GET|PUT|DELETE",
            "key": "string" (optional, will be prefixed with "recipes/"),
            "filename": "string" (optional, for PUT operations),
            "expiration": 3600 (optional, defaults to 3600 seconds)
        }
        """
        method = request.data.get("method")
        key = request.data.get("key", "")
        filename = request.data.get("filename")
        expiration = request.data.get("expiration", 3600)

        if not method:
            return Response({"error": "Method is required"}, status=status.HTTP_400_BAD_REQUEST)

        if method.upper() not in ["GET", "PUT", "DELETE"]:
            return Response(
                {"error": "Method must be GET, PUT, or DELETE"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not key.startswith("recipes/"):
            key = f"recipes/{key}" if key else "recipes"

        if method.upper() == "PUT" and filename:
            key = generate_key(key, filename)

        try:
            presigned_url = get_presigned_url(key, method, expiration)

            if not presigned_url:
                return Response(
                    {"error": "Failed to generate presigned URL"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Debug: Print the generated URL
            print(f"DEBUG: Generated presigned URL: {presigned_url}")
            print(f"DEBUG: Key: {key}")

            return Response(
                {
                    "presigned_url": presigned_url,
                    "key": key,
                    "method": method.upper(),
                    "expires_in": expiration,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Error generating presigned URL: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
