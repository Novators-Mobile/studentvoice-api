from django.urls import path
from . import views

urlpatterns = [
    path('meeting/', views.meeting_crud),
    path('meeting/<int:pk>/', views.meeting_detail),
    path('subject/<int:pk>/', views.subject_detail),
    path('teacher/', views.teacher_me)
]
