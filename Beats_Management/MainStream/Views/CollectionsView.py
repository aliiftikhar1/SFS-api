from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Beats_Management.MainStream.Serializers import BeatsCollectionsSerializer, BeatsCollectionAddSerializer, \
    BeatsCollectionRemoveSerializer, BeatsCollectionsDropdownSerializer, BeatsViewCollectionsFilesSerializer
from Beats_Management.models import BeatCollectionFiles
from Utilities import extract_error_messages, group_by_attribute
from Utilities.Enums import SubmissionStatus
from Utilities.Permissions import MemberPermissions


class CollectionsDropDownView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: BeatsCollectionsDropdownSerializer(many=True)})
    def get(request):
        """This function return the My Library Page Collections"""
        collections = request.user.collections.only("id", "name")
        collections_serializer = BeatsCollectionsDropdownSerializer(collections, many=True)
        return Response({'detail': collections_serializer.data}, status=status.HTTP_200_OK)


class ViewCollectionView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("product_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
    ], responses={200: BeatsViewCollectionsFilesSerializer(many=True)})
    def get(request):
        """This function return the My Library Page Collections"""
        product_type = request.GET.get("product_type")

        if not product_type:
            return Response({"detail": "product_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        collections_details = BeatCollectionFiles.objects. \
            select_related("beat", "collection", "audio_file"). \
            prefetch_related("beat__submissions",
                             "beat__submissions__supplier",
                             "beat__submissions__supplier__supplier_details",
                             "beat__submissions__supplier__supplier_details__artist"). \
            filter(collection__member=request.user, beat__submissions__beat_type=product_type,
                   beat__submissions__status=SubmissionStatus.APPROVED.value). \
            order_by("-created_at")

        collections_details_serializer = BeatsViewCollectionsFilesSerializer(collections_details, many=True)

        collections = request.user.collections.only("id", "name", "description")
        collections_serializer = BeatsCollectionsSerializer(collections, many=True)

        return Response({'detail': {
            "data": group_by_attribute(collections_details_serializer.data, "collection_id"),
            "collections": collections_serializer.data}},
            status=status.HTTP_200_OK
        )


class CollectionsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: BeatsCollectionsSerializer(many=True)})
    def get(request):
        """This function return the Collections"""
        collections = request.user.collections.only("id", "name", "description")
        collections_serializer = BeatsCollectionsSerializer(collections, many=True)
        return Response({'detail': collections_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=BeatsCollectionsSerializer(),
                         responses={201: "collection created successfully.", 400: "collection already exists."})
    def post(request):
        """This function create the My Library Page Collections"""
        collections_serializer = BeatsCollectionsSerializer(data=request.data, context={"user": request.user})
        collections_serializer.is_valid()
        if collections_serializer.errors:
            return Response({"detail": extract_error_messages(collections_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        collections_serializer.save()
        return Response({'detail': "collection created successfully."}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("collection_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("collection_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "collection deleted successfully", 404: "collection not found!"})
    def delete(request):
        """This function deletes the collection based on given id and name"""
        collection_id = request.GET.get("collection_id")
        collection_name = request.GET.get("collection_name")
        collection = request.user.collections.filter(id=collection_id, name=collection_name).first()
        if collection:
            try:
                collection.delete()
                return Response({"detail": "collection deleted successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "collection not found"}, status=status.HTTP_404_NOT_FOUND)


class CollectionsAddView(APIView):
    @staticmethod
    @swagger_auto_schema(request_body= BeatsCollectionAddSerializer(),
                         responses={201: "added to collection successfully.", 400: "collection not found."})
    def post(request):
        """This function create the My Library Page Collections"""
        collections_serializer = BeatsCollectionAddSerializer(data=request.data, context={"user": request.user})
        collections_serializer.is_valid()
        if collections_serializer.errors:
            return Response({"detail": extract_error_messages(collections_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        collections_serializer.save()
        return Response({'detail': "added to collection successfully."}, status=status.HTTP_201_CREATED)


class CollectionsRemoveView(APIView):
    @staticmethod
    @swagger_auto_schema(request_body= BeatsCollectionRemoveSerializer(),
                         responses={201: "removed from collection successfully.",
                                    404: "collection not found." or "beat not found." or "audio file not found."}
                         )
    def post(request):
        """This function create the My Library Page Collections"""
        collections_serializer = BeatsCollectionRemoveSerializer(data=request.data, context={"user": request.user})
        collections_serializer.is_valid()
        if collections_serializer.errors:
            return Response({"detail": extract_error_messages(collections_serializer.errors)},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': "remove from collection successfully."}, status=status.HTTP_200_OK)
