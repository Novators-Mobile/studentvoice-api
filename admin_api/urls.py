from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path('signup/', views.signup),
    path('checktoken/', views.check_token),
    path('university/', views.university_crud),
    path('university/<int:pk>/', views.university_detail),
    path('meeting/', views.meeting_crud),
    path('meeting/<int:pk>/', views.meeting_detail),
    path('subject/', views.subject_crud),
    path('subject/<int:pk>/', views.subject_detail),
    path('subject/<int:pk>/teacher/<int:teacher_id>/lecture/', views.subject_teacher_operations_lecture),
    path('subject/<int:pk>/teacher/<int:teacher_id>/practice/', views.subject_teacher_operations_practice),
    path('search/', views.search_all),
    path('teacher/', views.teacher_crud),
    path('teacher/<int:pk>/', views.teacher_detail)
]
