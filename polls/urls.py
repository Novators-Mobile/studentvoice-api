from django.urls import path
from . import views

urlpatterns = [
    path('', views.poll_crud),
    path('<int:pk>/', views.poll_detail),
    path('<int:poll_pk>/pollresults', views.poll_result_crud),
    path('noauth/<int:pk>/', views.poll_get),
    path('noauth/meeting/<int:poll_pk>/', views.meeting_get),
    path('noauth/<int:poll_pk>/pollresults', views.poll_result_post)
]