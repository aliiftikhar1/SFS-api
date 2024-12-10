from rest_framework import serializers

from Plan_Management.models import Pricing
from Utilities.Validators.InputValidator import InputValidator


class PricingSerializer(serializers.ModelSerializer):
    cents_per_point = serializers.FloatField(
        error_messages={"required": "cents_per_point is required", "blank": "cents_per_point cannot be blank"}
    )
    points_per_sample = serializers.IntegerField(
        error_messages={"required": "points_per_sample is required", "blank": "points_per_sample cannot be blank"}
    )
    points_per_midi = serializers.IntegerField(
        error_messages={"required": "points_per_midi is required", "blank": "points_per_midi cannot be blank"}
    )
    points_per_preset = serializers.IntegerField(
        error_messages={"required": "points_per_preset is required", "blank": "points_per_preset cannot be blank"}
    )
    non_profits_licence = serializers.IntegerField(
        error_messages={"required": "non_profits_licence is required", "blank": "non_profits_licence cannot be blank"}
    )
    commercial_licence = serializers.IntegerField(
        error_messages={"required": "commercial_licence is required", "blank": "commercial_licence cannot be blank"}
    )
    unlimited_licence = serializers.IntegerField(
        error_messages={"required": "unlimited_licence is required", "blank": "unlimited_licence cannot be blank"}
    )

    class Meta:
        model = Pricing
        exclude = ("id",)

    def validate(self, attrs):
        cents_per_point = attrs.get("cents_per_point")
        points_per_sample = attrs.get("points_per_sample")
        points_per_midi = attrs.get("points_per_midi")
        points_per_preset = attrs.get("points_per_preset")
        non_profits_licence = attrs.get("non_profits_licence")
        commercial_licence = attrs.get("commercial_licence")
        unlimited_licence = attrs.get("unlimited_licence")

        if not InputValidator(cents_per_point).is_valid():
            raise serializers.ValidationError("cents_per_point is required.")

        if cents_per_point < 0.0:
            raise serializers.ValidationError("cents_per_point must be a positive decimal.")

        if not InputValidator(points_per_sample).is_valid():
            raise serializers.ValidationError("points_per_sample is required.")

        if points_per_sample < 0:
            raise serializers.ValidationError("points_per_sample must be a positive number.")

        if not InputValidator(points_per_midi).is_valid():
            raise serializers.ValidationError("points_per_midi is required.")

        if points_per_midi < 0:
            raise serializers.ValidationError("points_per_midi must be a positive number.")

        if not InputValidator(points_per_preset).is_valid():
            raise serializers.ValidationError("points_per_preset is required.")

        if points_per_preset < 0:
            raise serializers.ValidationError("points_per_preset must be a positive number.")

        if not InputValidator(non_profits_licence).is_valid():
            raise serializers.ValidationError("non_profits_licence is required.")

        if non_profits_licence < 0:
            raise serializers.ValidationError("non_profits_licence must be a positive number.")

        if not InputValidator(commercial_licence).is_valid():
            raise serializers.ValidationError("commercial_licence is required.")

        if commercial_licence < 0:
            raise serializers.ValidationError("commercial_licence must be a positive number.")

        if not InputValidator(unlimited_licence).is_valid():
            raise serializers.ValidationError("unlimited_licence is required.")

        if unlimited_licence < 0:
            raise serializers.ValidationError("unlimited_licence must be a positive number.")

        return attrs

    def update(self, instance, validated_data):
        points_per_sample = validated_data.get("points_per_sample")
        cents_per_point = validated_data.get("cents_per_point")
        points_per_midi = validated_data.get("points_per_midi")
        points_per_preset = validated_data.get("points_per_preset")
        non_profits_licence = validated_data.get("non_profits_licence")
        commercial_licence = validated_data.get("commercial_licence")
        unlimited_licence = validated_data.get("unlimited_licence")

        update_fields = []

        if cents_per_point != instance.cents_per_point:
            instance.cents_per_point = cents_per_point
            update_fields.append("cents_per_point")

        if points_per_sample != instance.points_per_sample:
            instance.points_per_sample = points_per_sample
            update_fields.append("points_per_sample")

        if points_per_midi != instance.points_per_midi:
            instance.points_per_midi = points_per_midi
            update_fields.append("points_per_midi")

        if points_per_preset != instance.points_per_preset:
            instance.points_per_preset = points_per_preset
            update_fields.append("points_per_preset")

        if non_profits_licence != instance.non_profits_licence:
            instance.non_profits_licence = non_profits_licence
            update_fields.append("non_profits_licence")

        if commercial_licence != instance.commercial_licence:
            instance.commercial_licence = commercial_licence
            update_fields.append("commercial_licence")

        if unlimited_licence != instance.unlimited_licence:
            instance.unlimited_licence = unlimited_licence
            update_fields.append("unlimited_licence")

        instance.save(update_fields=update_fields)

        return instance
