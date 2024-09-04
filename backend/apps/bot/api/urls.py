from django.urls import path, include
from rest_framework import routers

from apps.bot.api import views

router = routers.DefaultRouter()
router.register("", views.RecommendationViewSet, basename="recommendation")

urlpatterns = [
    path(
        "snapshot_webhook_callback",
        views.snapshot_webhook_callback,
        name="snapshot_webhook_callback",
    ),
    path("", include(router.urls)),
]
