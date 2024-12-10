from rest_framework import serializers

from Beats_Management.models import BeatCollections, BeatAudioFiles, BeatCollectionFiles
from Utilities import generate_humanize_time
from Utilities.Enums import FileStatus, SubmissionStatus
from Utilities.Validators import InputValidator


class BeatsCollectionsDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeatCollections
        fields = ("id", "name")


class BeatsCollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeatCollections
        fields = ("id", "name", "description")

    def validate(self, attrs):
        name = attrs.get("name")
        description = attrs.get("description")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        if not InputValidator(description).is_valid():
            raise serializers.ValidationError("description is required.")

        user = self.context.get("user")

        collection = user.collections.filter(name=name, member=user).first()

        if collection:
            raise serializers.ValidationError("collection already exists")

        attrs["member"] = user
        return attrs


class BeatsCollectionAddSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField(
        error_messages={"required": "collection_id is required", "blank": "collection_id cannot be blank"}
    )
    collection_name = serializers.CharField(
        error_messages={"required": "collection_name is required", "blank": "collection_name cannot be blank"}
    )
    beat_id = serializers.IntegerField(
        error_messages={"required": "beat_id is required", "blank": "beat_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("collection_id", "collection_name", "beat_id", "audio_file_id")

    def validate(self, attrs):
        collection_id = attrs.pop("collection_id")
        collection_name = attrs.pop("collection_name")
        beat_id = attrs.pop("beat_id")
        audio_file_id = attrs.pop("audio_file_id")

        if not InputValidator(collection_name).is_valid():
            raise serializers.ValidationError("collection_name is required.")

        if not InputValidator(collection_id).is_valid():
            raise serializers.ValidationError("collection_id is required.")

        if not InputValidator(beat_id).is_valid():
            raise serializers.ValidationError("beat_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        audio_file = BeatAudioFiles.objects.prefetch_related("beats").filter(pk=audio_file_id,
                                                                         status=FileStatus.APPROVED.value).first()

        if not audio_file:
            raise serializers.ValidationError("audio file not found.")

        beat = audio_file.beats.first()

        if beat.id != beat_id and beat.submissions().first().status != SubmissionStatus.APPROVED.value:
            raise serializers.ValidationError("audio file not found.")

        user = self.context.get("user")

        collection = user.collections.filter(pk=collection_id, name=collection_name).first()

        if not collection:
            raise serializers.ValidationError("collection not found")

        attrs["collection"] = collection
        attrs["audio_file"] = audio_file
        attrs["beat"] = beat
        return attrs

    def create(self, validated_data):
        return BeatCollectionFiles.objects.get_or_create(**validated_data)


class BeatsCollectionRemoveSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField(
        error_messages={"required": "collection_id is required", "blank": "collection_id cannot be blank"}
    )
    collection_name = serializers.CharField(
        error_messages={"required": "collection_name is required", "blank": "collection_name cannot be blank"}
    )
    beat_id = serializers.IntegerField(
        error_messages={"required": "beat_id is required", "blank": "beat_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("collection_id", "collection_name", "beat_id", "audio_file_id")

    def validate(self, attrs):
        collection_id = attrs.pop("collection_id")
        collection_name = attrs.pop("collection_name")
        beat_id = attrs.pop("beat_id")
        audio_file_id = attrs.pop("audio_file_id")

        if not InputValidator(collection_name).is_valid():
            raise serializers.ValidationError("collection_name is required.")

        if not InputValidator(collection_id).is_valid():
            raise serializers.ValidationError("collection_id is required.")

        if not InputValidator(beat_id).is_valid():
            raise serializers.ValidationError("beat_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        collection_file = BeatCollectionFiles.objects.filter(collection__id=collection_id, audio_file__id=audio_file_id,
                                                         beat__id=beat_id).first()

        if not collection_file:
            raise serializers.ValidationError("file not found in given collection")

        collection_file.delete()

        return attrs


class BeatsViewCollectionsFilesSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField(source="collection.id")
    beat_id = serializers.IntegerField(source="beat.id")
    audio_file_id = serializers.IntegerField(source="audio_file.id")
    file = serializers.FileField(source="audio_file.file.file")
    file_name = serializers.CharField(source="audio_file.file.file_name")
    beat_name = serializers.CharField(source="beat.title")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    beats_artwork = serializers.FileField(source="beat.artwork")
    created_at = serializers.SerializerMethodField(method_name="get_created_at")

    class Meta:
        fields = ("collection_id", "beat_id", "audio_file_id", "file", "file_name", "beat_name", "artist", "artwork",
                  "created_at")

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
