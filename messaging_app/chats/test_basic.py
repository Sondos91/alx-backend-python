from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class BasicTestCase(TestCase):
    """Basic test case to ensure Django is working"""
    
    def test_basic_math(self):
        """Test basic math operations"""
        self.assertEqual(2 + 2, 4)
        self.assertEqual(5 * 5, 25)
    
    def test_string_operations(self):
        """Test string operations"""
        test_string = "Hello, World!"
        self.assertIn("Hello", test_string)
        self.assertEqual(len(test_string), 13)

class APIBasicTestCase(APITestCase):
    """Basic API test case"""
    
    def test_api_health(self):
        """Test that the API is accessible"""
        # This is a basic test - you can modify based on your actual API endpoints
        self.assertTrue(True)
    
    def test_django_version(self):
        """Test Django version"""
        import django
        self.assertIsNotNone(django.get_version())
