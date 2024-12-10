from rest_framework import serializers

from Product_Management.models import Genre, SubGenre
from Utilities.Validators.InputValidator import InputValidator


class SubGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubGenre
        fields = ("id", "name")


class GenreDropDownSerializer(serializers.ModelSerializer):
    sub_genre = SubGenreSerializer(many=True, read_only=True)

    class Meta:
        model = Genre
        fields = ("id", "name", "sub_genre")

    def validate(self, attrs):
        name = attrs.get("name")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        genre = Genre.objects.filter(name=name).first()

        if genre:
            raise serializers.ValidationError("genre already exists")

        return attrs


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    is_active = serializers.BooleanField(default=True)

    sub_genre = SubGenreSerializer(many=True, read_only=True)

    class Meta:
        model = Genre
        fields = ("id", "name", "is_active", "sub_genre")

    def validate(self, attrs):
        name = attrs.get("name")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        genre = Genre.objects.filter(name=name).first()

        if genre:
            raise serializers.ValidationError("genre already exists")

        return attrs


class CreateSubGenreSerializer(serializers.Serializer):
    genre_id = serializers.IntegerField(
        error_messages={
            "required": "genre_id is required",
            "blank": "genre_id cannot be blank",
        }
    )
    genre_name = serializers.CharField(
        error_messages={
            "required": "genre_name is required",
            "blank": "genre_name cannot be blank",
        }
    )
    sub_genre_name = serializers.CharField(
        error_messages={
            "required": "sub_genre_name is required",
            "blank": "sub_genre_name cannot be blank",
        }
    )

    def validate(self, attrs):
        genre_id = attrs.get("genre_id")
        genre_name = attrs.get("genre_name")
        sub_genre_name = attrs.get("sub_genre_name")

        if not InputValidator(genre_id).is_valid():
            raise serializers.ValidationError("genre_id is required.")

        if not InputValidator(genre_name).is_valid():
            raise serializers.ValidationError("genre_name is required.")

        if not InputValidator(sub_genre_name).is_valid():
            raise serializers.ValidationError("sub_genre_name is required.")

        genre = (
            Genre.objects.prefetch_related("sub_genre")
            .filter(pk=genre_id, name=genre_name)
            .first()
        )

        if not genre:
            raise serializers.ValidationError("genre not found")

        sub_genre = genre.sub_genre.filter(name=sub_genre_name).first()

        if sub_genre:
            raise serializers.ValidationError("sub genre already exists")

        attrs["genre"] = genre

        return attrs

    def create(self, validated_data):
        genre = validated_data.get("genre")
        sub_genre_name = validated_data.get("sub_genre_name")

        sub_genre = SubGenre.objects.create(genre=genre, name=sub_genre_name)
        return sub_genre
