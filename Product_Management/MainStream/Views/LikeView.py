from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Product_Management.MainStream.Serializers import UnLikesSerializer, LikesSerializer, ViewLikedFilesSerializer
from Product_Management.models import Likes
from Utilities import extract_error_messages
from Utilities.Permissions import MemberPermissions


class ViewLikesView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("product_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
    ], responses={200: ViewLikedFilesSerializer(many=True)})
    def get(request):
        """This function return the My Library Page likes Files"""
        product_type = request.GET.get("product_type")

        if not product_type:
            return Response({"detail": "product_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        likes = Likes.objects. \
            select_related("pack", "file"). \
            prefetch_related("pack__submissions",
                             "pack__submissions__supplier",
                             "pack__submissions__supplier__supplier_details",
                             "pack__submissions__supplier__supplier_details__artist"). \
            filter(pack__submissions__pack_type=product_type, member=request.user). \
            order_by("-created_at")
        likes_serializer = ViewLikedFilesSerializer(likes, many=True)
        return Response({'detail': likes_serializer.data}, status=status.HTTP_200_OK)


class LikeView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(request_body=LikesSerializer(),
                         responses={201: "file liked successfully.", 404: "file already liked."})
    def post(request):
        """This function likes an audio file"""
        like_serializer = LikesSerializer(data=request.data, context={"user": request.user})
        like_serializer.is_valid()
        if like_serializer.errors:
            return Response({"detail": extract_error_messages(like_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        like_serializer.save()
        return Response({'detail': "file liked successfully."}, status=status.HTTP_200_OK)


class UnlikeView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(request_body=UnLikesSerializer(),
                         responses={201: "file unliked successfully.", 404: "file not liked yet."})
    def post(request):
        """This function unlike an audio file"""
        unlike_serializer = UnLikesSerializer(data=request.data, context={"user": request.user})
        unlike_serializer.is_valid()
        if unlike_serializer.errors:
            return Response({"detail": extract_error_messages(unlike_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': "file unliked successfully."}, status=status.HTTP_200_OK)
