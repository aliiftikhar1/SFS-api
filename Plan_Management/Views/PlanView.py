from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Plan_Management.Serializers import CustomPlanSerializer, MonthlyAnnuallyPlanSerializer, PlansViewSerializer
from Plan_Management.models import Plan, PlanDetails
from Utilities import extract_error_messages
from Utilities.Enums import PlanStatus, PlanTypes, PlanDetailsTypes
from Utilities.Permissions import AdminPermissions


class PlansView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("timeline", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: PlansViewSerializer(many=True), 404: "invalid timeline!"})
    def get(request):
        timeline = request.GET.get('timeline')
        if timeline in PlanDetailsTypes.list():
            plan = PlanDetails.objects.select_related("plan").filter(timeline=timeline)
            plan_details_serializer = PlansViewSerializer(plan, many=True)
            return Response({'detail': plan_details_serializer.data}, status=status.HTTP_200_OK)
        return Response({"detail": "invalid timeline"}, status=status.HTTP_404_NOT_FOUND)


class CustomPlanView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: CustomPlanSerializer(many=True)})
    def get(request):
        """This function return all custom plans."""
        plan = Plan.objects.prefetch_related("details").filter(plan_type=PlanTypes.CUSTOM)
        plan_serializer = CustomPlanSerializer(plan, many=True)
        return Response({'detail': plan_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=CustomPlanSerializer(),
                         responses={200: "plan created successfully"})
    def post(request):
        """This function create custom plan based on given data"""
        plan_serializer = CustomPlanSerializer(data=request.data)
        plan_serializer.is_valid()
        if plan_serializer.errors:
            return Response({"detail": extract_error_messages(plan_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            plan_serializer.save()
        return Response({"detail": "plan created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(request_body=CustomPlanSerializer(),
                         responses={200: "plan updated successfully"})
    def put(request):
        """This function update custom plan based on given data"""
        plan_id = request.data.get("id")
        plan_name = request.data.get("name")
        plan = Plan.objects.prefetch_related("details").filter(pk=plan_id, name=plan_name).first()
        if plan:
            plan_serializer = CustomPlanSerializer(data=request.data, instance=plan)
            plan_serializer.is_valid()
            if plan_serializer.errors:
                return Response({"detail": extract_error_messages(plan_serializer.errors)},
                                status=status.HTTP_400_BAD_REQUEST)
            with transaction.atomic():
                plan_serializer.save()
            return Response({"detail": "plan updated successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "plan not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("plan_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("plan_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "plan status updated successfully", 404: "plan not found!"})
    def patch(request):
        """This function updates custom plan status based on given data"""
        plan_id = request.GET.get("plan_id")
        plan_name = request.GET.get("plan_name")

        plan = Plan.objects.filter(pk=plan_id, name=plan_name, plan_type=PlanTypes.CUSTOM).first()
        if plan:
            try:
                with transaction.atomic():
                    if plan.status == PlanStatus.ACTIVE:
                        plan.status = PlanStatus.PAUSE
                    else:
                        plan.status = PlanStatus.ACTIVE
                    plan.save(update_fields=["status"])
                return Response({"detail": "plan status updated successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "plan not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("plan_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("plan_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "plan deleted successfully", 404: "plan not found!"})
    def delete(request):
        """This function deletes custom plan based on given data"""
        plan_id = request.GET.get("plan_id")
        plan_name = request.GET.get("plan_name")

        plan = Plan.objects.prefetch_related("details").filter(pk=plan_id, name=plan_name,
                                                               plan_type=PlanTypes.CUSTOM).first()
        if plan:
            try:
                with transaction.atomic():
                    for detail in plan.details.all():
                        detail.delete()
                    plan.delete()
                return Response({"detail": "plan deleted successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "plan not found"}, status=status.HTTP_404_NOT_FOUND)


class MonthlyAnnuallyPlanView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: MonthlyAnnuallyPlanSerializer(many=True)})
    def get(request):
        """This function return all monthly/annual plans."""
        plan = Plan.objects.prefetch_related("details").filter(plan_type=PlanTypes.MONTHLY_ANNUALLY)
        plan_serializer = MonthlyAnnuallyPlanSerializer(plan, many=True)
        return Response({'detail': plan_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=MonthlyAnnuallyPlanSerializer(),
                         responses={200: "plan created successfully"})
    def post(request):
        """This function create monthly/annual plan based on given data"""
        plan_serializer = MonthlyAnnuallyPlanSerializer(data=request.data)
        plan_serializer.is_valid()
        if plan_serializer.errors:
            return Response({"detail": extract_error_messages(plan_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            plan_serializer.save()
        return Response({"detail": "plan created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(request_body=MonthlyAnnuallyPlanSerializer(),
                         responses={200: "plan updated successfully"})
    def put(request):
        """This function update monthly/annual plan based on given data"""
        plan_id = request.data.get("id")
        plan_name = request.data.get("name")
        plan = Plan.objects.prefetch_related("details").filter(pk=plan_id, name=plan_name).first()
        if plan:
            plan_serializer = MonthlyAnnuallyPlanSerializer(data=request.data, instance=plan)
            plan_serializer.is_valid()
            if plan_serializer.errors:
                return Response({"detail": extract_error_messages(plan_serializer.errors)},
                                status=status.HTTP_400_BAD_REQUEST)
            with transaction.atomic():
                plan_serializer.save()
            return Response({"detail": "plan updated successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "plan not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("plan_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("plan_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "plan status updated successfully", 404: "plan not found!"})
    def patch(request):
        """This function updates monthly/annual plan status based on given data"""
        plan_id = request.GET.get("plan_id")
        plan_name = request.GET.get("plan_name")

        plan = Plan.objects.filter(pk=plan_id, name=plan_name, plan_type=PlanTypes.MONTHLY_ANNUALLY).first()
        if plan:
            try:
                with transaction.atomic():
                    if plan.status == PlanStatus.ACTIVE:
                        plan.status = PlanStatus.PAUSE
                    else:
                        plan.status = PlanStatus.ACTIVE
                    plan.save(update_fields=["status"])
                return Response({"detail": "plan status updated successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "plan not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("plan_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("plan_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "plan deleted successfully", 404: "plan not found!"})
    def delete(request):
        """This function deletes monthly/annual plan based on given data"""
        plan_id = request.GET.get("plan_id")
        plan_name = request.GET.get("plan_name")

        plan = Plan.objects.prefetch_related("details").filter(pk=plan_id, name=plan_name,
                                                               plan_type=PlanTypes.CUSTOM).first()
        if plan:
            try:
                with transaction.atomic():
                    for detail in plan.details.all():
                        detail.delete()
                    plan.delete()
                return Response({"detail": "plan deleted successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "plan not found"}, status=status.HTTP_404_NOT_FOUND)
