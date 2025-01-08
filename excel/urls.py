from django.urls import path
from . import views

urlpatterns = [
    path('institute/<int:insitute_id>/subjects', views.institute_to_subject),
    path('institute/<int:insitute_id>/teachers', views.institute_to_teacher),
    path('subject/<int:subject_id>/teachers', views.subject_to_teacher),
    path('subject/<int:subject_id>/meetings', views.subject_to_meeting),
    path('teacher/<int:teacher_id>/subjects', views.teacher_to_subject),
    path('teacher/<int:teacher_id>/meetings', views.teacher_to_meeting)
]