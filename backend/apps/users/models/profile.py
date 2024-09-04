from textwrap import dedent

from django.db import models
from django.contrib.auth import get_user_model


class Profile(models.Model):
    """
    Profile represents the additional user profile information for each
    account in the application.

    This model is tightly coupled with the `apps.users.models.Account`
    model. When a new instance of `Account` is created and inserted into
    the `private.users_account` table, a trigger is executed which
    creates a corresponding profile for the account in the
    `private.users_profile` table, unless the account is a superuser.

    When a new instance of `apps.users.models.Account` is inserted, this
    SQL query is executed as a trigger on the `private.users_account`,
    creating a new instance of this model in `private.users_profile`:

    ```sql
    begin
      if (not new.is_superuser) then
        insert into private.users_profile (
          account_id,
          subscribed_to_emails,
          large_language_model
        )
        values
          (
            new.id,
            true,
            'gpt-4'
          );
        return new;
      else
        return nothing;
      end if;
    end;
    ```

    Attributes:
    -----------
    account : OneToOneField
        A one-to-one relationship with the Account model, making this
        the primary key for the Profile model. It ensures that each
        account has only one associated profile.
    first_name : CharField
        First name of the user. This field is optional.
    last_name : CharField
        Last name of the user. This field is optional.
    bio : TextField
        A brief bio of the user. This field is optional and can contain
        up to 500 characters.
    subscribed_to_emails : BooleanField
        Indicates if the user has subscribed to emails. Defaults to
        True, but is optional.
    large_language_model : CharField
        The preferred large language model of the user. Defaults to
        'gpt-4', but is optional. Provides choices between 'gpt-4' and
        'llama2' and will include more in the future.

    Methods:
    --------
    __str__() -> str:
        Returns the string representation of the user profile, which is
        the associated account's representation.
    """

    class LargeLanguageModelChoices(models.TextChoices):
        GPT_4 = "gpt-4"
        LLAMA2 = "llama2"

    account = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
        editable=False,
    )
    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=40, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    subscribed_to_emails = models.BooleanField(
        default=True, 
        null=True, 
        blank=True,
    )
    large_language_model = models.CharField(
        max_length=40,
        choices=LargeLanguageModelChoices.choices,
        default=LargeLanguageModelChoices.GPT_4,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.account.__str__()
