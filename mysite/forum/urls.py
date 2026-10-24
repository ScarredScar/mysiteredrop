from django.urls import path
from . import views

urlpatterns = [
    path('', views.topic_list, name='forum_topic_list'),
    path('new/', views.topic_create, name='forum_topic_create'),
    path('<int:pk>/', views.topic_detail, name='forum_topic_detail'),
    path('<int:pk>/delete/', views.topic_delete, name='forum_topic_delete'),
]