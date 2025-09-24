from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckTestCase(APITestCase):
    """Test the health check endpoint"""

    def test_health_check_endpoint(self):
        """Test that health check returns correct response"""
        url = reverse("core:health_check")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")
        self.assertEqual(response.data["message"], "Tasti API is running!")
        self.assertEqual(response.data["version"], "1.0.0")


class SettingsTestCase(TestCase):
    """Test basic Django configuration"""

    def test_installed_apps(self):
        """Test that required apps are installed"""
        from django.conf import settings

        required_apps = [
            "rest_framework",
            "corsheaders",
            "core",
        ]

        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)

    def test_environment_variables_loaded(self):
        """Test that environment variables work"""
        from django.conf import settings

        self.assertTrue(settings.SECRET_KEY)
        self.assertIsInstance(settings.DEBUG, bool)
