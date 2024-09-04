import datetime

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
import jwt

from apps.users.models import Account


class SupabaseAuthMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate users based on Supabase JWT
    (JSON Web Token) authorization.

    This middleware checks the 'Authorization' header in the incoming
    request for a JWT. If the JWT is present and valid, it sets the
    'user' attribute of the request to the corresponding user instance.
    If the JWT is invalid or not present, or if any exception occurs
    during the process, the 'user' attribute is set to an AnonymousUser.

    Methods:
    --------
    _return_anon_user(request: HttpRequest) -> HttpResponse:
        Sets the user attribute of the request to an AnonymousUser and
        returns the response.

    process_request(request: HttpRequest) -> HttpResponse:
        Processes the incoming request, checks for the 'Authorization'
        header, decodes the JWT, and sets the user accordingly.

    Attributes:
    -----------
    get_response : Callable
        A callable to get the response for a request. Typically set by
        Django's middleware mechanism.
    """

    def __init__(self, get_response):
        """
        Initializes the middleware.

        Parameters:
        -----------
        get_response : Callable
            A callable to get the response for a request.
        """
        self.get_response = get_response
        super().__init__(get_response)

    def _return_anon_user(self, request: HttpRequest):
        """
        Sets the user attribute of the request to an AnonymousUser and
        returns the response.

        Parameters:
        -----------
        request : HttpRequest
            The incoming request.

        Returns:
        --------
        HttpResponse
            The response for the request.
        """
        request.user = AnonymousUser()
        return self.get_response(request)

    def process_request(self, request: HttpRequest):
        """
        Processes the incoming request.

        This method checks for the 'Authorization' header in the
        request, decodes the JWT token, and sets the user attribute of
        the request to the corresponding user instance. If the JWT token
        is invalid or not present, or if any exception occurs, it sets
        the user attribute to an AnonymousUser.

        Parameters:
        -----------
        request : HttpRequest
            The incoming request.

        Returns:
        --------
        HttpResponse
            The response for the request.
        """
        if not isinstance(request.user, AnonymousUser):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            self._return_anon_user(request)

        try:
            token = auth_header.strip("Bearer").strip()
            decoded_token = jwt.decode(
                token,
                algorithms=["HS256"],
                options={
                    "verify_signature": False,
                },
            )

            if datetime.datetime.now().timestamp() > decoded_token["exp"]:
                self._return_anon_user(request)

            uuid = decoded_token["sub"]
            user = Account.objects.get(uuid=uuid)
            request.user = user

            return self.get_response(request)
        except (
            Account.DoesNotExist,
            ValidationError,
            KeyError,
            AttributeError,
        ):
            self._return_anon_user(request)
