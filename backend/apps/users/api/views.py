from http import HTTPStatus

from django.http import HttpRequest
from rest_framework import decorators, response, generics, mixins, permissions

from apps.users.models import Profile

from .serializers import AccountSerializer, ProfileSerializer


@decorators.api_view(["GET"])
def example(request: HttpRequest):
    return response.Response({"user": AccountSerializer(request.user).data})


class ProfileList(generics.GenericAPIView, mixins.ListModelMixin):
    """
    API view to list all user profiles. This view is restricted to admin
    users.

    Attributes:
    -----------
    queryset : QuerySet
        The set of all user profiles.
    serializer_class : Serializer
        The serializer to be used for profiles.
    permission_classes : List[Permission]
        The set of permissions required to access this view.

    Methods:
    --------
    get(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        Handles GET requests and returns a list of user profiles.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProfileDetail(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """
    API view to retrieve and update a specific user profile.

    Superusers don't have associated profiles and will receive an error
    message if they try to access their own profile. Regular
    authenticated users can retrieve and update their profile.

    Attributes:
    -----------
    queryset : QuerySet
        The set of all user profiles.
    serializer_class : Serializer
        The serializer to be used for profiles.
    permission_classes : List[Permission]
        The set of permissions required to access this view.

    Methods:
    --------
    get_object() -> Optional[Profile]:
        Retrieves the profile associated with the authenticated user.
        Returns None if the user is a superuser.

    get(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        Handles GET requests and returns the profile of the
        authenticated user.

    put(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        Handles PUT requests and updates the profile of the
        authenticated user.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieves the profile associated with the authenticated user."""
        if self.request.user.is_superuser:
            return None
        return Profile.objects.filter(account=self.request.user).first()

    def _superuser_detail(func):
        """
        Decorator that checks if the user is a superuser and returns an
        error response. Otherwise, proceeds to the decorated function.
        """

        def inner(self, request: HttpRequest):
            if request.user.is_superuser:
                return response.Response(
                    {
                        "detail": (
                            "The current user is a superuser and does not have"
                            " an associated profile"
                        )
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
            else:
                return func(self, request)

        return inner

    @_superuser_detail
    def get(self, request: HttpRequest, *args, **kwargs):
        """Handles GET requests and returns the profile of the authenticated user."""
        return self.retrieve(request, *args, **kwargs)

    @_superuser_detail
    def put(self, request: HttpRequest, *args, **kwargs):
        """
        Handles PUT requests to update the profile of the authenticated
        user. Restricts modification of certain fields ('account').
        """
        if any(field in request.data.keys() for field in ["account"]):
            return response.Response(
                {
                    "detail": (
                        "Either user profile property 'id' or 'account' cannot"
                        " be altered. Make sure the PUT request is not trying"
                        " to alter any of these fields."
                    )
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        return self.partial_update(request, *args, **kwargs)
