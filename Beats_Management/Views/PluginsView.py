from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Beats_Management.Serializers import PluginSerializer, PluginDropdownSerializer
from Beats_Management.models import BeatPlugin
from Utilities import extract_error_messages
from Utilities.Permissions import AdminPermissions, SupplierPermissions


class PluginsDropdownView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: PluginDropdownSerializer(many=True)})
    def get(request):
        """This function return the plugin dropdown list."""
        plugin = BeatPlugin.objects.all()
        plugin_serializer = PluginDropdownSerializer(plugin, many=True)
        return Response({'detail': plugin_serializer.data}, status=status.HTTP_200_OK)


class PluginsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: PluginSerializer(many=True)})
    def get(request):
        """This function return the plugin."""
        plugin = BeatPlugin.objects.all()
        plugin_serializer = PluginSerializer(plugin, many=True)
        return Response({'detail': plugin_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=PluginSerializer(),
                         responses={200: "plugin created successfully"})
    def post(request):
        """This function create the plugin based on given data"""
        plugin_serializer = PluginSerializer(data=request.data)
        plugin_serializer.is_valid()
        if plugin_serializer.errors:
            return Response({"detail": extract_error_messages(plugin_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        plugin_serializer.save()
        return Response({"detail": "plugin created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("plugin_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("plugin_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "plugin deleted successfully", 404: "plugin not found!"})
    def delete(request):
        """This function deletes the plugin based on given data"""
        plugin_id = request.GET.get("plugin_id")
        plugin_name = request.GET.get("plugin_name")
        plugin = BeatPlugin.objects.filter(pk=plugin_id, name=plugin_name).first()
        if plugin:
            try:
                plugin.delete()
                return Response({"detail": "plugin deleted successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "plugin not found"}, status=status.HTTP_404_NOT_FOUND)
