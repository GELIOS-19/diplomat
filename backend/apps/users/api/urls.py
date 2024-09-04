from django.urls import path

from .views import ProfileDetail, ProfileList

urlpatterns = [
    path(
        "profile/list",
        ProfileList.as_view(),
        name="profile_list",
    ),
    path(
        "profile",
        ProfileDetail.as_view(),
        name="profile",
    ),
]
