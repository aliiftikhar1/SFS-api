from rest_framework import serializers

from Beats_Management.models import BeatInstrument, BeatSubInstrument
from Utilities.Validators.InputValidator import InputValidator


class SubInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeatInstrument
        fields = ("id", "name")
        ref_name = 'BeatsManagement_subinstrument'


class InstrumentDropdownSerializer(serializers.ModelSerializer):
    sub_instrument = SubInstrumentSerializer(many=True, read_only=True)

    class Meta:
        model = BeatInstrument
        fields = ("id", "name", "sub_instrument")
        ref_name = 'BeatsManagement_instrumentdropdown'


class InstrumentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    is_active = serializers.BooleanField(default=True)

    sub_instrument = SubInstrumentSerializer(many=True, read_only=True)

    class Meta:
        model = BeatInstrument
        fields = ("id", "name", "is_active", "sub_instrument")
        ref_name = 'BeatsManagement_instrument'

    def validate(self, attrs):
        name = attrs.get("name")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        instrument = BeatInstrument.objects.filter(name=name).first()

        if instrument:
            raise serializers.ValidationError("instrument already exists")

        return attrs
    
    


class CreateSubInstrumentSerializer(serializers.Serializer):
    instrument_id = serializers.IntegerField(
        error_messages={
            "required": "instrument_id is required",
            "blank": "instrument_id cannot be blank",
        }
    )
    instrument_name = serializers.CharField(
        error_messages={
            "required": "instrument_name is required",
            "blank": "instrument_name cannot be blank",
        }
    )
    sub_instrument_name = serializers.CharField(
        error_messages={
            "required": "sub_instrument_name is required",
            "blank": "sub_instrument_name cannot be blank",
        }
    )

    def validate(self, attrs):
        instrument_id = attrs.get("instrument_id")
        instrument_name = attrs.get("instrument_name")
        sub_instrument_name = attrs.get("sub_instrument_name")

        if not InputValidator(instrument_id).is_valid():
            raise serializers.ValidationError("instrument_id is required.")

        if not InputValidator(instrument_name).is_valid():
            raise serializers.ValidationError("instrument_name is required.")

        if not InputValidator(sub_instrument_name).is_valid():
            raise serializers.ValidationError("sub_instrument_name is required.")

        instrument = (
            BeatInstrument.objects.prefetch_related("sub_instrument")
            .filter(pk=instrument_id, name=instrument_name)
            .first()
        )

        if not instrument:
            raise serializers.ValidationError("instrument not found")

        sub_instrument = instrument.sub_instrument.filter(name=sub_instrument_name).first()

        if sub_instrument:
            raise serializers.ValidationError("sub instrument already exists")

        attrs["instrument"] = instrument

        return attrs

    def create(self, validated_data):
        instrument = validated_data.get("instrument")
        sub_instrument_name = validated_data.get("sub_instrument_name")

        sub_instrument = BeatSubInstrument.objects.create(
            instrument=instrument, name=sub_instrument_name
        )
        return sub_instrument
    
    class Meta:
        ref_name = "BeatsManagement_CreateSubInstrumentSerializer"

