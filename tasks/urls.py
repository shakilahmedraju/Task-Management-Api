from django.urls import path
from tasks import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Task Management System API",
        default_version='v1',
        description="API documentation for Task Management System",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('register/', views.register, name='register'),
    path('tasks/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.get_task, name='get_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('users/<int:user_id>/', views.get_user, name='get_user'),
    path('users/<int:user_id>/tasks/', views.get_user_tasks, name='get_user_tasks'),
    path('tasks/<int:task_id>/assign/<int:user_id>/', views.assign_task, name='assign_task'),
    path('tasks/<int:task_id>/update_assigned_user/<int:user_id>/', views.update_assigned_user, name='update_assigned_user'),
    path('tasks/filter/', views.filter_tasks, name='filter_tasks'),
    path('tasks/sort/', views.sort_tasks, name='sort_tasks'),
    path('tasks/<int:task_id>/comments/', views.add_comment, name='add_comment'),
    path('tasks/<int:task_id>/comments/', views.get_comments, name='get_comments'),
    path('comments/<int:comment_id>/update/', views.update_comment, name='update_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]