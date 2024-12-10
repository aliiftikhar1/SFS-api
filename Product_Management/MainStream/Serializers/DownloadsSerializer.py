from django.db import transaction
from rest_framework import serializers

from Product_Management.models import AudioFiles, Pack, Downloads, FileDownloads
from Utilities import generate_humanize_time
from Utilities.Enums import FileStatus, SubmissionStatus
from Utilities.Validators import InputValidator


class DownloadsSerializer(serializers.Serializer):
    pack_id = serializers.IntegerField(
        error_messages={"required": "pack_id is required", "blank": "pack_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )
    complete_pack = serializers.BooleanField(
        error_messages={"required": "complete_pack is required", "blank": "complete_pack cannot be blank"},
        default=True
    )

    class Meta:
        fields = ("pack_id", "audio_file_id", "complete_pack")

    def validate(self, attrs):
        pack_id = attrs.get("pack_id")
        audio_file_id = attrs.get("audio_file_id")
        complete_pack = attrs.get("complete_pack")

        if not InputValidator(pack_id).is_valid():
            raise serializers.ValidationError("pack_id is required.")

        if not InputValidator(complete_pack).is_valid():
            raise serializers.ValidationError("complete_pack is required.")

        user = self.context.get("user")

        audio_files: list[AudioFiles] = []

        if not complete_pack:

            if not InputValidator(audio_file_id).is_valid():
                raise serializers.ValidationError("audio_file_id is required.")

            audio_file = AudioFiles.objects.prefetch_related("packs").filter(pk=audio_file_id,
                                                                             status=FileStatus.APPROVED.value).first()

            if not audio_file:
                raise serializers.ValidationError("audio file not found.")

            pack = audio_file.packs.first()

            if pack.id != pack_id and pack.submissions.all().first().status != SubmissionStatus.APPROVED.value:
                raise serializers.ValidationError("audio file not found in pack.")

            audio_files.append(audio_file)
        else:
            pack = Pack.objects.filter(pk=pack_id).first()

            if not pack or pack.submissions.all().first().status != SubmissionStatus.APPROVED.value:
                raise serializers.ValidationError("pack not found.")

            audio_files.extend(pack.audio_files.all())

        attrs["audio_files"] = audio_files
        attrs["pack"] = pack
        attrs["member"] = user
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            audio_files = validated_data.get("audio_files")
            pack = validated_data.get("pack")
            member = validated_data.get("member")

            pack.downloads_count += 1
            pack.save(update_fields=["downloads_count"])
            download = Downloads.objects.get_or_create(pack=pack, member=member)[0]
            for audio_file in audio_files:
                audio_file.downloads_count += 1
                audio_file.save(update_fields=["downloads_count"])
                FileDownloads.objects.get_or_create(download=download, audio_file=audio_file)

        return download


class ViewDownloadsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    pack_id = serializers.IntegerField(source="pack.id")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    title = serializers.CharField(source="pack.title")
    artwork = serializers.ImageField(source="pack.artwork")

    class Meta:
        fields = ("id", "pack_id", "artist", "title", "artwork")

    @staticmethod
    def get_artist(obj):
        submissions = obj.pack.submissions.all()[0]
        if submissions.supplier.is_admin:
            return submissions.supplier.get_user_details().name
        if submissions.supplier.is_supplier:
            return submissions.supplier.get_user_details().artist.name


class ViewFileDownloadsSerializer(serializers.Serializer):
    download_id = serializers.IntegerField(source="download.id")
    audio_file_id = serializers.IntegerField(source="audio_file.id")
    file = serializers.FileField(source="audio_file.file.file")
    file_name = serializers.CharField(source="audio_file.file.file_name")
    pack_name = serializers.CharField(source="download.pack.title")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    artwork = serializers.FileField(source="download.pack.artwork")
    created_at = serializers.SerializerMethodField(method_name="get_created_at")

    class Meta:
        fields = ("download_id", "audio_file_id", "file", "file_name", "pack_name", "artist", "artwork", "created_at")

    @staticmethod
    def get_created_at(obj):
        return generate_humanize_time(obj.created_at)

    @staticmethod
    def get_artist(obj):
        submissions = obj.download.pack.submissions.all()[0]
        if submissions.supplier.is_admin:
            return submissions.supplier.get_user_details().name
        if submissions.supplier.is_supplier:
            return submissions.supplier.get_user_details().artist.name
