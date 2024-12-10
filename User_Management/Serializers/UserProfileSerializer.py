from rest_framework import serializers

from User_Management.models import AdminOrStaff, Member, Supplier
from Utilities.Validators.InputValidator import InputValidator


class SupplierProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField(source='supplier_user.email')
    verified = serializers.BooleanField(read_only=True, required=False, source='supplier_user.verified')

    class Meta:
        model = Supplier
        fields = ("first_name", "last_name", "username", "email", "verified")

    def validate(self, attrs):
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")

        if not InputValidator(first_name).is_valid():
            raise serializers.ValidationError("first_name is required.")

        if not InputValidator(last_name).is_valid():
            raise serializers.ValidationError("last_name is required.")

        return attrs

    def update(self, instance, validated_data):
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")

        self.instance.first_name = first_name
        self.instance.last_name = last_name
        self.instance.save(update_fields=["first_name", "last_name"])
        return instance


class MemberProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    country = serializers.CharField()
    city_or_state = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField(source='member_user.email')
    verified = serializers.BooleanField(read_only=True, required=False, source='member_user.verified')

    class Meta:
        model = Member
        fields = ("name", "country", "city_or_state", "username", "email", "verified")

    def validate(self, attrs):
        name = attrs.get("name")
        country = attrs.get("country")
        city_or_state = attrs.get("city_or_state")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        if not InputValidator(country).is_valid():
            raise serializers.ValidationError("country is required.")

        if not InputValidator(city_or_state).is_valid():
            raise serializers.ValidationError("city_or_state is required.")

        return attrs

    def update(self, instance, validated_data):
        name = validated_data.get("name")
        country = validated_data.get("country")
        city_or_state = validated_data.get("city_or_state")

        self.instance.name = name
        self.instance.country = country
        self.instance.city_or_state = city_or_state
        self.instance.save(update_fields=["name", "country", "city_or_state"])
        return instance


class AdminOrStaffProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField(source="admin_user.email")
    verified = serializers.BooleanField(read_only=True, required=False, source="admin_user.verified")

    class Meta:
        model = AdminOrStaff
        fields = ("name", "username", "email", "verified")

    def validate(self, attrs):
        name = attrs.get("name")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        return attrs

    def update(self, instance, validated_data):
        name = validated_data.get("name")

        self.instance.name = name
        self.instance.save(update_fields=["name"])
        return instance
