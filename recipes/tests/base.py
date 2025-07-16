from django.test import TestCase
from django.contrib.auth.models import User

class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_user()

    @classmethod
    def create_user(cls):
        user = User.objects.create_user(username='testuser',
                                        password='testpassword',
                                        email='testuser@example.com')
        return user