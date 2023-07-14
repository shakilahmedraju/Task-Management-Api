from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

class UserEndpointsTestCase(APITestCase):
    def test_register_user(self):
        url = '/api/register/'
        data = {'username': 'testuser', 'password': 'testpass'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_register_user_missing_data(self):
        url = '/api/register/'
        data = {'username': 'testuser'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_get_user(self):
        self.client.login(username='testuser', password='testpass')
        url = f'/api/users/{self.user.id}/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    # Add more tests for other user endpoints
