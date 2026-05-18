from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.submit_url, name='submit_url'),
    path('status/<str:task_id>/', views.task_status, name='task_status'),
]