from pathlib import Path

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
import markdown

from .recommendation import Recommendation


@receiver(post_save, sender=Recommendation)
def send_recommendation_summary_email(
    sender, instance: Recommendation, created, **kwargs
):
    """
    Sends a summary email of a recommendation after it has been saved.

    This function is a signal receiver that gets triggered post the save
    event of a `Recommendation` instance. If the recommendation is newly
    created, it extracts the proposal details and the recommendation
    content and sends a formatted email to the associated account.

    Args:
    ----
    sender : Model
        The model class that triggered the signal.
    instance : Recommendation
        The actual instance of `Recommendation` that got saved.
    created : bool
        A flag indicating if the instance was created or just updated.
    **kwargs : dict
        Additional keyword arguments passed by the signal trigger.

    Note:
    ----
    The function is decorated with `@receiver`, which connects it to the
    post_save signal of the `Recommendation` model. Thus, it will be
    automatically called every time a `Recommendation` instance is
    saved.
    """
    if created:
        with open(
            Path(__file__).parent.parent
            / "text_templates"
            / "emails"
            / "recommendation_summary.txt",
            "r",
        ) as email_file:
            email = email_file.read().format(
                proposal_title=instance.proposal["title"],
                proposal_body=instance.proposal["body"],
                diplomat_recommendation=instance.recommendation,
                total_tokens=instance.usage["total_tokens"],
            )

        send_mail(
            subject=(
                "Diplomat proposal recommendation for"
                f" {instance.proposal['title']}"
            ),
            message=email,
            from_email=settings.EMAIL_HOST,
            recipient_list=[instance.account.email],
            html_message=markdown.markdown(email),
        )
