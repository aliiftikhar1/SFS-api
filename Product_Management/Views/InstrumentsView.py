from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Product_Management.Serializers import InstrumentSerializer, SubInstrumentSerializer, \
    CreateSubInstrumentSerializer, InstrumentDropdownSerializer
from Product_Management.models import Instrument
from Utilities import extract_error_messages
from Utilities.Permissions import AdminPermissions, SupplierPermissions


class InstrumentsDropdownView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: InstrumentDropdownSerializer(many=True)})
    def get(request):
        """This function return the instrument dropdown list."""
        instrument = Instrument.objects.prefetch_related("sub_instrument").all()
        instrument_serializer = InstrumentDropdownSerializer(instrument, many=True)
        return Response({'detail': instrument_serializer.data}, status=status.HTTP_200_OK)


class InstrumentsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: InstrumentSerializer(many=True)})
    def get(request):
        """This function return the instrument."""
        instrument = Instrument.objects.prefetch_related("sub_instrument").all()
        instrument_serializer = InstrumentSerializer(instrument, many=True)
        return Response({'detail': instrument_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=SubInstrumentSerializer(),
                         responses={200: "instrument created successfully"})
    def post(request):
        """This function create the instrument based on given data"""
        instrument_serializer = InstrumentSerializer(data=request.data)
        instrument_serializer.is_valid()
        if instrument_serializer.errors:
            return Response({"detail": extract_error_messages(instrument_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        instrument_serializer.save()
        return Response({"detail": "instrument created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("instrument_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("instrument_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "instrument deleted successfully", 404: "instrument not found!"})
    def delete(request):
        """This function deletes the instrument based on given data"""
        instrument_id = request.GET.get("instrument_id")
        instrument_name = request.GET.get("instrument_name")
        instrument = Instrument.objects.filter(pk=instrument_id, name=instrument_name).first()
        if instrument:
            try:
                instrument.delete()
                return Response({"detail": "instrument deleted successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "instrument not found"}, status=status.HTTP_404_NOT_FOUND)


class SubInstrumentsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("instrument_id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
        openapi.Parameter("instrument_name", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True)
    ], responses={200: SubInstrumentSerializer()})
    def get(request):
        """This function return the sub-instruments."""
        instrument_id = request.GET.get("instrument_id")
        instrument_name = request.GET.get("instrument_name")
        instrument = Instrument.objects.prefetch_related("sub_instrument").filter(pk=instrument_id,
                                                                                  name=instrument_name).first()
        if instrument:
            sub_instrument = instrument.sub_instrument.all()
            sub_instrument_serializer = SubInstrumentSerializer(sub_instrument, many=True)
            return Response({'detail': sub_instrument_serializer.data}, status=status.HTTP_200_OK)
        return Response({"detail": "instrument not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(request_body=CreateSubInstrumentSerializer(),
                         responses={200: "sub instrument created successfully"})
    def post(request):
        """This function create the sub-instrument based on given data"""
        sub_instrument_serializer = CreateSubInstrumentSerializer(data=request.data)
        sub_instrument_serializer.is_valid()
        if sub_instrument_serializer.errors:
            return Response({"detail": extract_error_messages(sub_instrument_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        sub_instrument_serializer.save()
        return Response({"detail": "sub instrument created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("instrument_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("instrument_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("sub_instrument_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("sub_instrument_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "sub instrument deleted successfully", 404: "sub instrument not found!"})
    def delete(request):
        """This function deletes the sub-instrument based on given data"""
        instrument_id = request.GET.get("instrument_id")
        instrument_name = request.GET.get("instrument_name")
        sub_instrument_id = request.GET.get("sub_instrument_id")
        sub_instrument_name = request.GET.get("sub_instrument_name")
        instrument = Instrument.objects.prefetch_related("sub_instrument").filter(pk=instrument_id,
                                                                                  name=instrument_name).first()
        if instrument:
            sub_instrument = instrument.sub_instrument.filter(pk=sub_instrument_id, name=sub_instrument_name)
            if sub_instrument:
                try:
                    sub_instrument.delete()
                    return Response({"detail": "sub instrument deleted successfully"}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "sub instrument not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "instrument not found"}, status=status.HTTP_404_NOT_FOUND)
