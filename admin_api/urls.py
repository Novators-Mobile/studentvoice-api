from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path('signup/', views.signup),
    path('checktoken/', views.check_token),
    path('university/', views.university_crud),
    path('university/<int:pk>/', views.university_detail)
]
