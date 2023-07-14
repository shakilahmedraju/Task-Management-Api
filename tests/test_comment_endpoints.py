from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Task, Comment

class CommentEndpointsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.task = Task.objects.create(title='Test Task', description='Test Description', due_date='2023-12-31', assignee=self.user)
        self.client.login(username='testuser', password='testpass')

    def test_add_comment(self):
        url = f'/api/tasks/{self.task.id}/comments/'
        data = {'content': 'Test Comment'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, 'Test Comment')

    def test_add_comment_invalid_task(self):
        url = '/api/tasks/999/comments/'
        data = {'content': 'Test Comment'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Comment.objects.count(), 0)

    # Add more tests for other comment endpoints
