from rest_framework import serializers

from apps.bot.models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Recommendation` model.

    Provides a means to convert `Recommendation` model instances into
    easily interpretable and renderable formats such as JSON or XML.
    This serializer is set up to use all fields from the
    `Recommendation` model.

    Attributes:
    -----------
    Meta : class
        A nested class that defines metadata options for the serializer.
        It specifies the model to serialize (`Recommendation`) and the
        fields to include in the serialized output (all fields in this
        case).
    """

    class Meta:
        model = Recommendation
        fields = "__all__"
