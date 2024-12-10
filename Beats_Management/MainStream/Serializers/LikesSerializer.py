from django.db import transaction
from rest_framework import serializers

from Beats_Management.models import BeatAudioFiles, BeatLikes
from Utilities import generate_humanize_time
from Utilities.Validators import InputValidator


class BeatsLikesSerializer(serializers.Serializer):
    beat_id = serializers.IntegerField(
        error_messages={"required": "beat_id is required", "blank": "beat_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("beat_id", "audio_file_id")

    def validate(self, attrs):
        beat_id = attrs.get("beat_id")
        audio_file_id = attrs.get("audio_file_id")

        if not InputValidator(beat_id).is_valid():
            raise serializers.ValidationError("beat_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        user = self.context.get("user")

        audio_file = BeatAudioFiles.objects.prefetch_related("beats").filter(pk=audio_file_id).first()

        if not audio_file:
            raise serializers.ValidationError("audio file not found.")

        beat = audio_file.beats.first()

        if beat.id != beat_id:
            raise serializers.ValidationError("audio file not found in beat.")

        like = BeatLikes.objects.select_related("file").filter(file__id=audio_file_id, beat__id=beat_id,
                                                           member=user).first()

        if like:
            raise serializers.ValidationError("Beat already liked.")

        attrs["audio_file"] = audio_file
        attrs["beat"] = beat
        attrs["member"] = user
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            audio_file = validated_data.get("audio_file")
            beat = validated_data.get("beat")
            member = validated_data.get("member")

            (like, created) = BeatLikes.objects.get_or_create(beat=beat, file=audio_file, member=member)
            if created:
                audio_file.likes_count += 1
                audio_file.save(update_fields=["likes_count"])

        return like


class BeatsUnLikesSerializer(serializers.Serializer):
    beat_id = serializers.IntegerField(
        error_messages={"required": "beat_id is required", "blank": "beat_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("beat_id", "audio_file_id")

    def validate(self, attrs):
        beat_id = attrs.get("beat_id")
        audio_file_id = attrs.get("audio_file_id")

        if not InputValidator(beat_id).is_valid():
            raise serializers.ValidationError("beat_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        user = self.context.get("user")

        like = BeatLikes.objects.select_related("file").filter(file__id=audio_file_id, beat__id=beat_id,
                                                           member=user).first()

        if not like:
            raise serializers.ValidationError("file not liked yet.")

        like.file.likes_count -= 1
        like.file.save(update_fields=["likes_count"])

        like.delete()
        return attrs


class BeatsViewLikedFilesSerializer(serializers.Serializer):
    like_id = serializers.IntegerField(source="id")
    file_id = serializers.IntegerField(source="file.file.id")
    file = serializers.FileField(source="file.file.file")
    file_name = serializers.CharField(source="file.file.file_name")
    beat_name = serializers.CharField(source="beat.title")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    beats_artwork = serializers.FileField(source="beat.beats_artwork")
    created_at = serializers.SerializerMethodField(method_name="get_created_at")

    class Meta:
        fields = ("like_id", "file_id", "file", "file_name", "beat_name", "artist", "beats_artwork", "created_at")

    @staticmethod
    def get_created_at(obj):
        return generate_humanize_time(obj.created_at)

    @staticmethod
    def get_artist(obj):
        submissions = obj.beat.submissions.all()[0]
        if submissions.supplier.is_admin:
            return submissions.supplier.get_user_details().name
        if submissions.supplier.is_supplier:
            return submissions.supplier.get_user_details().artist.name
