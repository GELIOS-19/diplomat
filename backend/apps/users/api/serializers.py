from rest_framework import serializers

from apps.users.models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model.

    This serializer converts complex types, like Account instances, into
    a format that's easy to render into a JSON response. It provides
    serialization for a subset of the Account model's fields, including
    the UUID, email, username, and various user permissions.

    Attributes:
    -----------
    Meta : class
        Metadata class that defines the model to serialize and the
        fields to include in the serialized representation.
    """

    class Meta:
        model = Account
        fields = (
            "uuid",
            "email",
            "username",
            "is_active",
            "is_staff",
            "is_superuser",
        )


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    This serializer converts complex types, like Profile instances,
    into a format that's easy to render into a JSON response. It
    provides serialization for all fields of the Profile model.

    Attributes:
    -----------
    Meta : class
        Metadata class that defines the model to serialize and specifies
        that all fields of the model should be included in the
        serialized representation.
    """

    class Meta:
        model = Account
        fields = "__all__"
