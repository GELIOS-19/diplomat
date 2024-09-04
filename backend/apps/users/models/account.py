from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from apps.users.supabase_client import supabase_client


class AccountManager(BaseUserManager):
    """
    AccountManager is a custom user manager for the Account model. It
    provides methods to create a regular user and a superuser for the
    application.

    Methods:
    --------
    create_user(
        email: str, password: str, username: Optional[str] = None
    ) -> Account:
        Creates and returns a new user with the given email and
        password. If a username is not provided, it defaults to the
        user's UUID.

    create_superuser(
        email: str, password: str, username: Optional[str] = None
    ) -> Account:
        Creates and returns a new superuser with the given email and
        password. This user will have is_staff, is_active, and
        is_superuser flags set to True. If a username is not provided,
        it defaults to the user's UUID.
    """

    def create_user(self, email, password, username=None):
        supabase_client.auth.sign_up({"email": email, "password": password})

        user: Account = Account.objects.get(email=email)

        if not username:
            username = str(user.uuid)

        user.username = username
        user.save()

        return user

    def create_superuser(self, email, password, username=None):
        user: Account = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )

        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()

        return user


class Account(AbstractBaseUser, PermissionsMixin):
    """
    Account represents a user in the application, extending both the
    AbstractBaseUser and PermissionsMixin. It is integrated with
    Supabase's authentication system.

    This model is tightly coupled with Supabase's `auth.users` table.
    When a user registers through Supabase, a trigger is set on the
    `auth.users` table which creates a new instance of this model in
    the `private.users_account` table. Similarly, when a user confirms
    their email, another trigger updates the `is_active` field of the
    corresponding `users_account` row.

    When a new user is registered through Supabase, the following SQL
    query is executed as a trigger on the `auth.users` table, creating
    a new instance of this model in `private.users_account`:

    ```sql
    begin
      insert into private.users_account (
        uuid,
        email,
        password,
        username,
        is_staff,
        is_active,
        is_superuser,
        created_at
      )
      values
        (
          new.id,
          new.email,
          concat('bcrypt$', new.encrypted_password),
          new.id::text,
          false,
          false,
          false,
          now()
        )
      on conflict do nothing;
      return new;
    end;
    ```

    When a user confirms their email address, the following SQL query
    is executed as a trigger on the `auth.users` table, updating the
    `is_active` field of the corresponding `users_account` row:

    ```sql
    begin
      if (
        old.email_confirmed_at is null
        and new.email_confirmed_at is not null
      ) then
        update private.users_account
        set
          is_active = true
        where uuid = new.id;
      end if;
      return new;
    end;
    ```

    Attributes:
    -----------
    uuid : UUIDField
        Unique user identifier which is not editable.
    email : EmailField
        Email of the user, which also serves as the unique identifier
        for authentication.
    username : CharField
        Unique username of the user. Can be blank, but has a maximum
        length of 36 characters.
    is_staff : BooleanField
        Indicates if the user is a staff member. Defaults to False.
    is_active : BooleanField
        Indicates if the user is active. Defaults to False. Set to True
        once the user confirms their email.
    created_at : DateTimeField
        Timestamp of when the user account was created.

    Methods:
    --------
    get_short_name() -> str:
        Returns the username of the user.

    delete():
        Deletes the user from both the Supabase authentication system
        and the local database.

    __str__() -> str:
        Returns the email of the user for string representation.
    """

    uuid = models.UUIDField(unique=True, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=36, unique=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = AccountManager()

    def get_short_name(self):
        """
        Returns the username of the user.

        Returns:
        --------
        str:
            The username of the user.
        """
        return self.username

    def delete(self):
        """
        Deletes the user from both the Supabase authentication system
        and the local database.

        The method ensures that when a user is deleted from the Django
        ORM, they are also deleted from Supabase's authentication
        system.
        """
        supabase_client.auth.admin.delete_user(self.uuid)
        super().delete()

    def __str__(self):
        """
        String representation of the user.

        Returns:
        --------
        str:
            The email of the user.
        """
        return self.email
