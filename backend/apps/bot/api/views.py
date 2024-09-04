from http import HTTPStatus

from rest_framework import decorators, response, permissions, viewsets
from django.http import HttpRequest

from apps.bot.models import Recommendation
from apps.bot.api.serializers import RecommendationSerializer
from apps.bot.snapshot import query_snapshot_proposal
from apps.bot import completions
from apps.users.models import Profile


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def snapshot_webhook_callback(request: HttpRequest):
    """
    Handles the webhook callback from Snapshot.

    This function processes incoming proposals from Snapshot. For each
    user profile with a personal statement, it constructs a completion
    request, sends it to the desired language model, and then stores the
    model's response as a recommendation.

    Parameters:
    ----------
    request : HttpRequest
        The incoming request containing the proposal information.

    Returns:
    -------
    Response
        An HTTP response indicating the success or failure of the
        operation.
    """
    try:
        proposal_id = request.data["id"].strip("proposal/")
        proposal = query_snapshot_proposal(proposal_id)["proposal"]
    except KeyError:
        return response.Response(status=HTTPStatus.BAD_REQUEST)

    profiles = Profile.objects.exclude(bio__isnull=True).exclude(bio__exact="")

    for profile in profiles:
        match profile.large_language_model:
            case Profile.LargeLanguageModelChoices.GPT_4:
                completion_response = completions.openai_provider_completion(
                    completions.CompletionRequest(
                        profile,
                        proposal,
                    )
                )
                bot_response = Recommendation(
                    account=profile.account,
                    profile=profile,
                    proposal={
                        "title": proposal["title"],
                        "body": proposal["body"],
                    },
                    recommendation=completion_response.completion,
                    usage=completion_response.usage.__dict__,
                )
                bot_response.save()

    return response.Response(status=HTTPStatus.OK)


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and manipulating Recommendation objects.

    This ViewSet provides CRUD operations for `Recommendation`
    instances. If the request user is a superuser, they can access all
    recommendations. Otherwise, users can only access their own
    recommendations.

    Attributes:
    -----------
    serializer_class : RecommendationSerializer
        The serializer class used for converting `Recommendation`
        instances to and from JSON format.

    Methods:
    --------
    get_queryset() -> QuerySet:
        Retrieves a queryset of `Recommendation` instances based on the
        permissions of the request user.
    """

    serializer_class = RecommendationSerializer

    def get_queryset(self):
        """
        Determines the set of recommendations that the user is allowed
        to view.

        If the user is a superuser, they can see all recommendations.
        Otherwise, they can only see their own recommendations.

        Returns:
        -------
        QuerySet
            A queryset of `Recommendation` instances.
        """
        if self.request.user.is_superuser:
            queryset = Recommendation.objects.all()
        else:
            queryset = Recommendation.objects.filter(account=self.request.user)
        return queryset
