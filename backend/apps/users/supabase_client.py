from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import supabase

try:
    supabase_client = supabase.Client(
        settings.SUPABASE["URL"],
        settings.SUPABASE["SERVICE_ROLE_KEY"],
        options=supabase.client.ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )
except (KeyError, AttributeError):
    raise ImproperlyConfigured(
        "Either the `SUPABASE` setting is missing or it is improperly"
        " configured"
    )
