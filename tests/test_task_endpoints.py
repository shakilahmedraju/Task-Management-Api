from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Task

class TaskEndpointsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_create_task(self):
        url = '/api/tasks/'
        data = {'title': 'Test Task', 'description': 'Test Description', 'due_date': '2023-12-31', 'assignee': self.user.id}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'Test Task')

    def test_create_task_missing_data(self):
        url = '/api/tasks/'
        data = {'title': 'Test Task', 'description': 'Test Description'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.count(), 0)

    # Add more tests for other task endpoints
