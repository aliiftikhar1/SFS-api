from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Beats_Management.MainStream.Serializers import BeatsUnLikesSerializer, BeatsLikesSerializer, BeatsViewLikedFilesSerializer
from Beats_Management.models import BeatLikes
from Utilities import extract_error_messages
from Utilities.Permissions import MemberPermissions


class ViewLikesView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("product_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
    ], responses={200: BeatsViewLikedFilesSerializer(many=True)})
    def get(request):
        """This function return the My Library Page likes Files"""
        product_type = request.GET.get("product_type")

        if not product_type:
            return Response({"detail": "product_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        likes = BeatLikes.objects. \
            select_related("beat", "file"). \
            prefetch_related("beat__submissions",
                             "beat__submissions__supplier",
                             "beat__submissions__supplier__supplier_details",
                             "beat__submissions__supplier__supplier_details__artist"). \
            filter(beat__submissions__beat_type=product_type, member=request.user). \
            order_by("-created_at")
        likes_serializer = BeatsViewLikedFilesSerializer(likes, many=True)
        return Response({'detail': likes_serializer.data}, status=status.HTTP_200_OK)


class LikeView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(request_body= BeatsLikesSerializer(),
                         responses={201: "file liked successfully.", 404: "file already liked."})
    def post(request):
        """This function likes an audio file"""
        like_serializer = BeatsLikesSerializer(data=request.data, context={"user": request.user})
        like_serializer.is_valid()
        if like_serializer.errors:
            return Response({"detail": extract_error_messages(like_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        like_serializer.save()
        return Response({'detail': "file liked successfully."}, status=status.HTTP_200_OK)


class UnlikeView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(request_body= BeatsUnLikesSerializer(),
                         responses={201: "file unliked successfully.", 404: "file not liked yet."})
    def post(request):
        """This function unlike an audio file"""
        unlike_serializer = BeatsUnLikesSerializer(data=request.data, context={"user": request.user})
        unlike_serializer.is_valid()
        if unlike_serializer.errors:
            return Response({"detail": extract_error_messages(unlike_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': "file unliked successfully."}, status=status.HTTP_200_OK)
