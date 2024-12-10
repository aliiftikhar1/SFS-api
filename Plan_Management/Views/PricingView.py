from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Plan_Management.Serializers import PricingSerializer
from Plan_Management.models import Pricing
from Utilities import extract_error_messages
from Utilities.Permissions import AdminPermissions


class PricingView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: PricingSerializer()})
    def get(request):
        """This function return all pricing details."""
        pricing = Pricing.objects.filter(pk=1).first()
        pricing_serializer = PricingSerializer(pricing)
        return Response({'detail': pricing_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=PricingSerializer(),
                         responses={200: "pricing updated successfully"})
    def put(request):
        """This function update pricing based on given data"""
        pricing = Pricing.objects.filter(pk=1).first()
        pricing_serializer = PricingSerializer(data=request.data, instance=pricing)
        pricing_serializer.is_valid()
        if pricing_serializer.errors:
            return Response({"detail": extract_error_messages(pricing_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            pricing_serializer.save()
        return Response({"detail": "pricing updated successfully"}, status=status.HTTP_200_OK)
