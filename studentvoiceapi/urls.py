"""
URL configuration for studentvoiceapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi

class APISchemeGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.base_path = '/api/'
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="StudentVoice API",
        default_version="v1",
        description="api for StudentVoice project",
    ),
    url="https://novatorsmobile.ru/api/",
    generator_class=APISchemeGenerator,
    public=True,
    permission_classes=[permissions.AllowAny]
)

urlpatterns = [
    path('admin_api/', include('admin_api.urls')),
    path('teacher_api/', include('teacher_api.urls')),
    path('polls/', include('polls.urls')),
    path('excel/', include('excel.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
