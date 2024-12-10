from rest_framework import serializers

from Product_Management.models import Plugin
from Utilities.Validators.InputValidator import InputValidator


class PluginDropdownSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    extension = serializers.CharField()

    class Meta:
        model = Plugin
        fields = ("id", "name", "extension")


class PluginSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    extension = serializers.CharField(
        error_messages={
            "required": "extension is required",
            "blank": "extension cannot be blank",
        }
    )
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Plugin
        fields = ("id", "name", "extension", "is_active")

    def validate(self, attrs):
        name = attrs.get("name")
        extension = attrs.get("extension")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        if not InputValidator(extension).is_valid():
            raise serializers.ValidationError("extension is required.")

        plugin = Plugin.objects.filter(name=name).first()

        if plugin:
            raise serializers.ValidationError("plugin already exists")

        return attrs
