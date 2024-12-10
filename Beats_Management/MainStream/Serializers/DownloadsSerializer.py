from django.db import transaction
from rest_framework import serializers

from Beats_Management.models import BeatAudioFiles, Beats, BeatDownloads, BeatFileDownloads
from Utilities import generate_humanize_time
from Utilities.Enums import FileStatus, SubmissionStatus
from Utilities.Validators import InputValidator


class BeatsDownloadsSerializer(serializers.Serializer):
    beat_id = serializers.IntegerField(
        error_messages={"required": "beat_id is required", "blank": "beat_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )
    complete_beat = serializers.BooleanField(
        error_messages={"required": "complete_beat is required", "blank": "complete_beat cannot be blank"},
        default=True
    )

    class Meta:
        fields = ("beat_id", "audio_file_id", "complete_beat")

    def validate(self, attrs):
        beat_id = attrs.get("beat_id")
        audio_file_id = attrs.get("audio_file_id")
        complete_beat = attrs.get("complete_beat")

        if not InputValidator(beat_id).is_valid():
            raise serializers.ValidationError("beat_id is required.")

        if not InputValidator(complete_beat).is_valid():
            raise serializers.ValidationError("complete_beat is required.")

        user = self.context.get("user")

        audio_files: list[BeatAudioFiles] = []

        if not complete_beat:

            if not InputValidator(audio_file_id).is_valid():
                raise serializers.ValidationError("audio_file_id is required.")

            audio_file = BeatAudioFiles.objects.prefetch_related("beats").filter(pk=audio_file_id,
                                                                             status=FileStatus.APPROVED.value).first()

            if not audio_file:
                raise serializers.ValidationError("audio file not found.")

            beat = audio_file.beats.first()

            if beat.id != beat_id and beat.submissions.all().first().status != SubmissionStatus.APPROVED.value:
                raise serializers.ValidationError("audio file not found in beat.")

            audio_files.append(audio_file)
        else:
            beat = Beats.objects.filter(pk=beat_id).first()

            if not beat or beat.submissions.all().first().status != SubmissionStatus.APPROVED.value:
                raise serializers.ValidationError("beat not found.")

            audio_files.extend(beat.audio_files.all())

        attrs["audio_files"] = audio_files
        attrs["beat"] = beat
        attrs["member"] = user
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            audio_files = validated_data.get("audio_files")
            beat = validated_data.get("beat")
            member = validated_data.get("member")

            beat.downloads_count += 1
            beat.save(update_fields=["downloads_count"])
            download = BeatDownloads.objects.get_or_create(beat=beat, member=member)[0]
            for audio_file in audio_files:
                audio_file.downloads_count += 1
                audio_file.save(update_fields=["downloads_count"])
                BeatFileDownloads.objects.get_or_create(download=download, audio_file=audio_file)

        return download


class BeatsViewDownloadsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    beat_id = serializers.IntegerField(source="beat.id")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    title = serializers.CharField(source="beat.title")
    artwork = serializers.ImageField(source="beat.artwork")

    class Meta:
        fields = ("id", "beat_id", "artist", "title", "artwork")

    @staticmethod
    def get_artist(obj):
        submissions = obj.beat.submissions.all()[0]
        if submissions.supplier.is_admin:
            return submissions.supplier.get_user_details().name
        if submissions.supplier.is_supplier:
            return submissions.supplier.get_user_details().artist.name


class BeatsViewFileDownloadsSerializer(serializers.Serializer):
    download_id = serializers.IntegerField(source="download.id")
    audio_file_id = serializers.IntegerField(source="audio_file.id")
    file = serializers.FileField(source="audio_file.file.file")
    file_name = serializers.CharField(source="audio_file.file.file_name")
    beat_name = serializers.CharField(source="download.beat.title")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    artwork = serializers.FileField(source="download.beat.artwork")
    created_at = serializers.SerializerMethodField(method_name="get_created_at")

    class Meta:
        fields = ("download_id", "audio_file_id", "file", "file_name", "beat_name", "artist", "artwork", "created_at")

    @staticmethod
    def get_created_at(obj):
        return generate_humanize_time(obj.created_at)

    @staticmethod
    def get_artist(obj):
        submissions = obj.download.beat.submissions.all()[0]
        if submissions.supplier.is_admin:
            return submissions.supplier.get_user_details().name
        if submissions.supplier.is_supplier:
            return submissions.supplier.get_user_details().artist.name
