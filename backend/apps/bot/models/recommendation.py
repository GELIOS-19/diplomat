from django.db import models
from django.contrib.auth import get_user_model

from apps.users.models import Profile


class Recommendation(models.Model):
    """
    Represents a recommendation generated for a user based on their
    interactions.

    This model captures the recommendation data that arises from
    processing user input through a language model or other algorithms.
    It associates each recommendation with a specific account and
    profile, and stores the messages that led to the recommendation, as
    well as the completion or output of the recommendation process.

    Attributes:
    -----------
    account : ForeignKey
        The associated account for whom the recommendation was made.
        It relates to the user model and ensures that if the user is
        deleted, the recommendation is also deleted.
    profile : ForeignKey
        The profile associated with the account. It captures more
        detailed information about the user and ensures that if the
        profile is deleted, the recommendation is also deleted.
    proposal : JSONField
        A JSON-structured field that captures the initial proposal or
        input that led to this recommendation.
    recommendation : TextField
        A field that captures the output or result of the recommendation
        process, which can be the direct response from a language model
        or other algorithms.
    usage : JSONField
        A JSON-structured field that captures the token usage that the
        completion api call incurred.
    created_at : DateTimeField
        The timestamp when the recommendation was created.
    """

    account = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        unique=False,
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        unique=False,
    )
    proposal = models.JSONField()
    recommendation = models.TextField()
    usage = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
