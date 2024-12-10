from rest_framework import serializers

from Beats_Management.models import BeatMood
from Utilities.Validators.InputValidator import InputValidator


class BeatMoodsDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeatMood
        fields = ("id", "name")


class BeatMoodSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = BeatMood
        fields = ("id", "name", "is_active")

    def validate(self, attrs):
        name = attrs.get("name")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        mood = BeatMood.objects.filter(name=name).first()

        if mood:
            raise serializers.ValidationError("mood already exists")

        return attrs
