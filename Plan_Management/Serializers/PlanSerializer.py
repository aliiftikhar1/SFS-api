from rest_framework import serializers

from Plan_Management.models import Plan, PlanDetails
from Utilities import extract_error_messages
from Utilities.Enums import PlanTypes, PlanDetailsTypes
from Utilities.Validators.InputValidator import InputValidator


def validate_plan_details(attrs):
    pricing = attrs.get("pricing")
    points = attrs.get("points")
    timeline = attrs.get("timeline")

    if not InputValidator(pricing).is_valid():
        raise serializers.ValidationError("pricing is required.")

    if not InputValidator(points).is_valid():
        raise serializers.ValidationError("points is required.")

    if not InputValidator(timeline).is_valid():
        raise serializers.ValidationError("timeline is required.")

    if not InputValidator(timeline).is_valid_option(PlanDetailsTypes.list()):
        raise serializers.ValidationError("timeline is not valid.")

    return attrs


def create_plan_details(validated_data):
    pricing = validated_data.get("pricing")
    points = validated_data.get("points")
    timeline = validated_data.get("timeline")
    return PlanDetails.objects.create(pricing=pricing, points=points, timeline=timeline, plan=None)


def update_plan_details(instance, validated_data):
    pricing = validated_data.get("pricing")
    points = validated_data.get("points")
    timeline = validated_data.get("timeline")

    instance.pricing = pricing
    instance.points = points
    instance.timeline = timeline
    instance.save(update_fields=["pricing", "points", "timeline"])
    return instance


class CustomPlanDetailsSerializer(serializers.ModelSerializer):
    pricing = serializers.IntegerField(
        error_messages={"required": "pricing is required", "blank": "pricing cannot be blank"}
    )
    points = serializers.IntegerField(
        error_messages={"required": "points is required", "blank": "points cannot be blank"}
    )
    timeline = serializers.CharField(
        error_messages={"required": "timeline is required", "blank": "timeline cannot be blank"}
    )
    currency = serializers.CharField(
        error_messages={"required": "currency is required", "blank": "currency cannot be blank"},
        read_only=True, required=False
    )
    duration = serializers.IntegerField(
        error_messages={"required": "duration is required", "blank": "duration cannot be blank"},
    )

    class Meta:
        model = PlanDetails
        fields = ("id", "pricing", "points", "timeline", "currency", "duration")

    def validate(self, attrs):
        attrs = validate_plan_details(attrs)
        duration = attrs.get("duration")

        if not InputValidator(duration).is_valid():
            raise serializers.ValidationError("duration is required.")

        if duration < 1:
            raise serializers.ValidationError("duration should be at-least one day.")

        return attrs

    def create(self, validated_data):
        duration = validated_data.get("duration")
        custom_plan_details = create_plan_details(validated_data)
        custom_plan_details.duration = duration
        custom_plan_details.save(update_fields=["duration"])
        return custom_plan_details

    def update(self, instance, validated_data):
        duration = validated_data.get("duration")
        updated_plan_details = update_plan_details(instance, validated_data)
        updated_plan_details.duration = duration
        updated_plan_details.save(update_fields=["duration"])
        return instance


class MonthlyAnnuallyPlanDetailsSerializer(serializers.ModelSerializer):
    pricing = serializers.IntegerField(
        error_messages={"required": "pricing is required", "blank": "pricing cannot be blank"}
    )
    points = serializers.IntegerField(
        error_messages={"required": "points is required", "blank": "points cannot be blank"}
    )
    timeline = serializers.CharField(
        error_messages={"required": "timeline is required", "blank": "timeline cannot be blank"}
    )
    currency = serializers.CharField(
        error_messages={"required": "currency is required", "blank": "currency cannot be blank"},
        read_only=True, required=False
    )

    class Meta:
        model = PlanDetails
        fields = ("id", "pricing", "points", "timeline", "currency")

    def validate(self, attrs):
        return validate_plan_details(attrs)

    def create(self, validated_data):
        return create_plan_details(validated_data)

    def update(self, instance, validated_data):
        return update_plan_details(instance, validated_data)


def create_plan(validated_data):
    plan_details = validated_data.get("plan_details")
    name = validated_data.get("name")
    plan_type = validated_data.get("plan_type")

    plan = Plan.objects.create(name=name, plan_type=plan_type)
    for detail in plan_details:
        detail.plan = plan
        detail.save()

    return plan


def update_plan(instance, validated_data):
    plan_details = validated_data.get("plan_details")
    name = validated_data.get("name")
    plan_type = validated_data.get("plan_type")

    instance.name = name
    instance.plan_type = plan_type
    instance.save()

    for detail in plan_details:
        detail.plan = instance
        detail.save(update_fields=["plan"])

    return instance


class CustomPlanSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    details = CustomPlanDetailsSerializer(many=True)
    plan_type = serializers.CharField(
        error_messages={"required": "plan_type is required", "blank": "plan_type cannot be blank"}
    )
    status = serializers.CharField(
        error_messages={"required": "status is required", "blank": "status cannot be blank"},
        read_only=True, required=False
    )

    class Meta:
        model = Plan
        fields = ("id", "name", "plan_type", "details", "status")

    def validate(self, attrs):
        name = attrs.get("name")
        details = attrs.get("details")
        plan_type = attrs.get("plan_type")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        if not InputValidator(plan_type).is_valid():
            raise serializers.ValidationError("plan_type is required.")

        if not InputValidator(plan_type).is_(PlanTypes.CUSTOM):
            raise serializers.ValidationError("plan_type is invalid.")

        if len(details) != 1:
            raise serializers.ValidationError("Custom Plan must have one timeline.")

        if not self.instance:
            plan = Plan.objects.filter(name=name).first()

            if plan:
                raise serializers.ValidationError("plan already exists")

        plan_details_serializer = CustomPlanDetailsSerializer(data=details, many=True)
        plan_details_serializer.is_valid()

        if plan_details_serializer.errors:
            raise serializers.ValidationError(extract_error_messages(plan_details_serializer.errors))

        plan_details = []
        if self.instance:
            for detail in self.instance.details.all():
                plan_details_serializer = CustomPlanDetailsSerializer(data=details[0], instance=detail)
                plan_details_serializer.is_valid()
                plan_details.append(plan_details_serializer.save())
        else:
            plan_details = plan_details_serializer.save()

        attrs["plan_details"] = plan_details
        return attrs

    def create(self, validated_data):
        return create_plan(validated_data)

    def update(self, instance, validated_data):
        return update_plan(instance, validated_data)


class MonthlyAnnuallyPlanSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    details = MonthlyAnnuallyPlanDetailsSerializer(many=True)
    plan_type = serializers.CharField(
        error_messages={"required": "plan_type is required", "blank": "plan_type cannot be blank"}
    )
    status = serializers.CharField(
        error_messages={"required": "status is required", "blank": "status cannot be blank"},
        read_only=True, required=False
    )

    class Meta:
        model = Plan
        fields = ("id", "name", "plan_type", "details", "status")

    def validate(self, attrs):
        plan_type = attrs.get("plan_type")
        name = attrs.get("name")
        details = attrs.get("details")

        if not InputValidator(plan_type).is_valid():
            raise serializers.ValidationError("plan_type is required.")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        if not InputValidator(plan_type).is_(PlanTypes.MONTHLY_ANNUALLY):
            raise serializers.ValidationError("plan_type is invalid.")

        if len(details) != 2:
            raise serializers.ValidationError("Monthly/Annually Plan must have two timelines.")

        if not self.instance:
            plan = Plan.objects.filter(name=name).first()

            if plan:
                raise serializers.ValidationError("plan already exists")

        plan_details_serializer = MonthlyAnnuallyPlanDetailsSerializer(data=details, many=True)
        plan_details_serializer.is_valid()

        if plan_details_serializer.validated_data[0].get("timeline") == plan_details_serializer.validated_data[1].get(
                "timeline"):
            raise serializers.ValidationError("Monthly/Annually Plan must have Monthly and Yearly.")

        if plan_details_serializer.errors:
            raise serializers.ValidationError(extract_error_messages(plan_details_serializer.errors))

        plan_details = []
        if self.instance:
            for detail in self.instance.details.all():
                for d in details:
                    if d.get("timeline") == detail.timeline:
                        plan_details_serializer = MonthlyAnnuallyPlanDetailsSerializer(data=details[0],
                                                                                       instance=detail)
                        plan_details_serializer.is_valid()
                        plan_details.append(plan_details_serializer.save())
        else:
            plan_details = plan_details_serializer.save()

        attrs["plan_details"] = plan_details
        return attrs

    def create(self, validated_data):
        return create_plan(validated_data)

    def update(self, instance, validated_data):
        return update_plan(instance, validated_data)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class PlansViewSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()

    class Meta:
        model = PlanDetails
        fields = "__all__"
