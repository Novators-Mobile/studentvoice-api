from django.urls import path
from . import views

urlpatterns = [
    path('meeting/<int:meeting_pk>/form', views.form_detail)
]