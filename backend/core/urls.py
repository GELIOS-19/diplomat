"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
import os

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

_api = "apps.{}.api.urls".format

schema_view = get_schema_view(
    openapi.Info(
        title="Diplomat API",
        default_version=os.getenv("DIPLOMAT_API_VERSION"),
    ),
    public=True,
    permission_classes=[
        permissions.AllowAny,
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        f"api/{os.getenv('DIPLOMAT_API_VERSION')}/docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger",
    ),
    path(
        f"api/{os.getenv('DIPLOMAT_API_VERSION')}/users/",
        include(_api("users")),
    ),
    path(
        f"api/{os.getenv('DIPLOMAT_API_VERSION')}/bot/",
        include(_api("bot")),
    ),
]
