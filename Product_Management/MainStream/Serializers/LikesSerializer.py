from django.db import transaction
from rest_framework import serializers

from Product_Management.models import AudioFiles, Likes
from Utilities import generate_humanize_time
from Utilities.Validators import InputValidator


class LikesSerializer(serializers.Serializer):
    pack_id = serializers.IntegerField(
        error_messages={"required": "pack_id is required", "blank": "pack_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("pack_id", "audio_file_id")

    def validate(self, attrs):
        pack_id = attrs.get("pack_id")
        audio_file_id = attrs.get("audio_file_id")

        if not InputValidator(pack_id).is_valid():
            raise serializers.ValidationError("pack_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        user = self.context.get("user")

        audio_file = AudioFiles.objects.prefetch_related("packs").filter(pk=audio_file_id).first()

        if not audio_file:
            raise serializers.ValidationError("audio file not found.")

        pack = audio_file.packs.first()

        if pack.id != pack_id:
            raise serializers.ValidationError("audio file not found in pack.")

        like = Likes.objects.select_related("file").filter(file__id=audio_file_id, pack__id=pack_id,
                                                           member=user).first()

        if like:
            raise serializers.ValidationError("file already liked.")

        attrs["audio_file"] = audio_file
        attrs["pack"] = pack
        attrs["member"] = user
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            audio_file = validated_data.get("audio_file")
            pack = validated_data.get("pack")
            member = validated_data.get("member")

            (like, created) = Likes.objects.get_or_create(pack=pack, file=audio_file, member=member)
            if created:
                audio_file.likes_count += 1
                audio_file.save(update_fields=["likes_count"])

        return like


class UnLikesSerializer(serializers.Serializer):
    pack_id = serializers.IntegerField(
        error_messages={"required": "pack_id is required", "blank": "pack_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("pack_id", "audio_file_id")

    def validate(self, attrs):
        pack_id = attrs.get("pack_id")
        audio_file_id = attrs.get("audio_file_id")

        if not InputValidator(pack_id).is_valid():
            raise serializers.ValidationError("pack_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        user = self.context.get("user")

        like = Likes.objects.select_related("file").filter(file__id=audio_file_id, pack__id=pack_id,
                                                           member=user).first()

        if not like:
            raise serializers.ValidationError("file not liked yet.")

        like.file.likes_count -= 1
        like.file.save(update_fields=["likes_count"])

        like.delete()
        return attrs


class ViewLikedFilesSerializer(serializers.Serializer):
    like_id = serializers.IntegerField(source="id")
    file_id = serializers.IntegerField(source="file.file.id")
    file = serializers.FileField(source="file.file.file")
    file_name = serializers.CharField(source="file.file.file_name")
    pack_name = serializers.CharField(source="pack.title")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    artwork = serializers.FileField(source="pack.artwork")
    created_at = serializers.SerializerMethodField(method_name="get_created_at")

    class Meta:
        fields = ("like_id", "file_id", "file", "file_name", "pack_name", "artist", "artwork", "created_at")

    @staticmethod
    def get_created_at(obj):
        return generate_humanize_time(obj.created_at)

    @staticmethod
    def get_artist(obj):
        submissions = obj.pack.submissions.all()[0]
        if submissions.supplier.is_admin:
            return submissions.supplier.get_user_details().name
        if submissions.supplier.is_supplier:
            return submissions.supplier.get_user_details().artist.name
