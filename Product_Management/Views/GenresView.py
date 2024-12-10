from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Product_Management.Serializers import GenreSerializer, SubGenreSerializer, CreateSubGenreSerializer, \
    GenreDropDownSerializer
from Product_Management.models import Genre
from Utilities import extract_error_messages
from Utilities.Permissions import AdminPermissions, SupplierPermissions


class GenresDropdownView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: GenreDropDownSerializer(many=True)})
    def get(request):
        """This function return the genres dropdown"""
        genre = Genre.objects.prefetch_related("sub_genre").all()
        genre_serializer = GenreDropDownSerializer(genre, many=True)
        return Response({'detail': genre_serializer.data}, status=status.HTTP_200_OK)


class GenresView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: GenreSerializer(many=True)})
    def get(request):
        """This function return the genre."""
        genre = Genre.objects.prefetch_related("sub_genre").all()
        genre_serializer = GenreSerializer(genre, many=True)
        return Response({'detail': genre_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=SubGenreSerializer(),
                         responses={200: "genre created successfully"})
    def post(request):
        """This function create the genre based on given data"""
        genre_serializer = GenreSerializer(data=request.data)
        genre_serializer.is_valid()
        if genre_serializer.errors:
            return Response({"detail": extract_error_messages(genre_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        genre_serializer.save()
        return Response({"detail": "genre created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("genre_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("genre_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "genre deleted successfully", 404: "genre not found!"})
    def delete(request):
        """This function deletes the genre based on given data"""
        genre_id = request.GET.get("genre_id")
        genre_name = request.GET.get("genre_name")
        genre = Genre.objects.filter(pk=genre_id, name=genre_name).first()
        if genre:
            try:
                genre.delete()
                return Response({"detail": "genre deleted successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "genre not found"}, status=status.HTTP_404_NOT_FOUND)


class SubGenresView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("genre_id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
        openapi.Parameter("genre_name", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True)
    ], responses={200: SubGenreSerializer()})
    def get(request):
        """This function return the sub-genres."""
        genre_id = request.GET.get("genre_id")
        genre_name = request.GET.get("genre_name")
        genre = Genre.objects.prefetch_related("sub_genre").filter(pk=genre_id, name=genre_name).first()
        if genre:
            sub_genre = genre.sub_genre.all()
            sub_genre_serializer = SubGenreSerializer(sub_genre, many=True)
            return Response({'detail': sub_genre_serializer.data}, status=status.HTTP_200_OK)
        return Response({"detail": "genre not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(request_body=CreateSubGenreSerializer(),
                         responses={200: "sub genre created successfully"})
    def post(request):
        """This function create the sub-genre based on given data"""
        sub_genre_serializer = CreateSubGenreSerializer(data=request.data)
        sub_genre_serializer.is_valid()
        if sub_genre_serializer.errors:
            return Response({"detail": extract_error_messages(sub_genre_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        sub_genre_serializer.save()
        return Response({"detail": "sub genre created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("genre_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("genre_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("sub_genre_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("sub_genre_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "sub genre deleted successfully", 404: "sub genre not found!"})
    def delete(request):
        """This function deletes the sub-genre based on given data"""
        genre_id = request.GET.get("genre_id")
        genre_name = request.GET.get("genre_name")
        sub_genre_id = request.GET.get("sub_genre_id")
        sub_genre_name = request.GET.get("sub_genre_name")
        genre = Genre.objects.prefetch_related("sub_genre").filter(pk=genre_id, name=genre_name).first()
        if genre:
            sub_genre = genre.sub_genre.filter(pk=sub_genre_id, name=sub_genre_name)
            if sub_genre:
                try:
                    sub_genre.delete()
                    return Response({"detail": "sub genre deleted successfully"}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "sub genre not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "genre not found"}, status=status.HTTP_404_NOT_FOUND)
