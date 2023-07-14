from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Task, Comment
from .serializers import TaskSerializer, UserSerializer, CommentSerializer
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination

class TaskPagination(PageNumberPagination):
    page_size = 10  # Number of tasks per page
    page_size_query_param = 'page_size'
    max_page_size = 100



class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.userprofile.role in ['admin', 'manager']

class IsTeammember(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.userprofile.role in ['admin', 'manager', 'team_member']

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.assignee == request.user



@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        try:
            user = User.objects.create_user(username=username, password=password)
            token, _ = Token.objects.get_or_create(user=user)  # Create or retrieve existing token
            return Response({'message': 'User created successfully.', 'token': token.key})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    else:
        return Response({'error': 'Invalid request.'}, status=400)





@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_task(request):
    serializer = TaskSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrManager, IsTeammember])
def get_task(request, task_id):
    """
    Retrieve a task by ID.

    Parameters:
    - task_id: The ID of the task to retrieve.

    Returns:
    - 200 OK: Task data if the task exists.
    - 404 Not Found: If the task does not exist.
    """
    try:
        task = Task.objects.get(pk=task_id)
        paginator = TaskPagination()
        result_page = paginator.paginate_queryset([task], request)
        serializer = TaskSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=404)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly, IsTeammember])
def update_task(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
        serializer = TaskSerializer(instance=task, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly, IsTeammember])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
        task.delete()
        return Response(status=204)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeammember])
def get_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeammember])
def get_user_tasks(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        tasks = user.assigned_tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_task(request, task_id, user_id):
    try:
        task = Task.objects.get(pk=task_id)
        user = User.objects.get(pk=user_id)
        task.assignee = user
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    except (Task.DoesNotExist, User.DoesNotExist):
        return Response({'error': 'Task or User not found.'}, status=404)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_assigned_user(request, task_id, user_id):
    try:
        task = Task.objects.get(pk=task_id)
        user = User.objects.get(pk=user_id)
        task.assignee = user
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    except (Task.DoesNotExist, User.DoesNotExist):
        return Response({'error': 'Task or User not found.'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_tasks(request):
    assigned_to_user = request.GET.get('assigned_to_user')
    completed = request.GET.get('completed')
    due_date = request.GET.get('due_date')

    tasks = Task.objects.all()

    if assigned_to_user:
        tasks = tasks.filter(assignee_id=assigned_to_user)

    if completed:
        tasks = tasks.filter(completed=completed)

    if due_date:
        tasks = tasks.filter(due_date=due_date)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sort_tasks(request):
    sort_by = request.GET.get('sort_by')
    tasks = Task.objects.all()

    if sort_by == 'due_date':
        tasks = tasks.order_by('due_date')
    elif sort_by == 'priority':
        tasks = tasks.order_by('-priority')
    elif sort_by == 'title':
        tasks = tasks.order_by('title')

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)





@api_view(['POST'])
def add_comment(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(task=task, commenter=request.user)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=404)

@api_view(['GET'])
def get_comments(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=404)

@api_view(['PUT'])
def update_comment(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
        serializer = CommentSerializer(instance=comment, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found.'}, status=404)

@api_view(['DELETE'])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
        comment.delete()
        return Response(status=204)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found.'}, status=404)
