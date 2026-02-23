import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models.user import User


class UserProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='admin',
            company_id=uuid.uuid4(),
            phone_number='1234567890',
        )

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')

    def test_get_profile_unauthenticated(self):
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put('/auth/profile/', {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '9876543210',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        self.assertEqual(response.data['phone_number'], '9876543210')

    def test_patch_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/auth/profile/', {
            'first_name': 'Patched',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Patched')
        self.assertEqual(response.data['last_name'], 'User')

    def test_profile_read_only_fields_not_updated(self):
        self.client.force_authenticate(user=self.user)
        original_email = self.user.email
        original_role = self.user.role
        response = self.client.put('/auth/profile/', {
            'email': 'newemail@example.com',
            'role': 'super_admin',
            'first_name': 'Test',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], original_email)
        self.assertEqual(response.data['role'], original_role)
