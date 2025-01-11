from django.urls import path
from . import views

urlpatterns = [
    path('meeting/', views.meeting_crud),
    path('meeting/<int:pk>/', views.meeting_detail),
    path('subject/<int:pk>/', views.subject_detail),
    path('subject/', views.get_teacher_subjects),
    path('meeting/<int:meeting_id>/participants', views.get_polls_participants),
    path('teacher/', views.teacher_me)
]
