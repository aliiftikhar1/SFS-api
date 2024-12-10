from rest_framework import serializers

from Product_Management.models import Collections, AudioFiles, CollectionFiles
from Utilities import generate_humanize_time
from Utilities.Enums import FileStatus, SubmissionStatus
from Utilities.Validators import InputValidator


class CollectionsDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collections
        fields = ("id", "name")


class CollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collections
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


class CollectionAddSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField(
        error_messages={"required": "collection_id is required", "blank": "collection_id cannot be blank"}
    )
    collection_name = serializers.CharField(
        error_messages={"required": "collection_name is required", "blank": "collection_name cannot be blank"}
    )
    pack_id = serializers.IntegerField(
        error_messages={"required": "pack_id is required", "blank": "pack_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("collection_id", "collection_name", "pack_id", "audio_file_id")

    def validate(self, attrs):
        collection_id = attrs.pop("collection_id")
        collection_name = attrs.pop("collection_name")
        pack_id = attrs.pop("pack_id")
        audio_file_id = attrs.pop("audio_file_id")

        if not InputValidator(collection_name).is_valid():
            raise serializers.ValidationError("collection_name is required.")

        if not InputValidator(collection_id).is_valid():
            raise serializers.ValidationError("collection_id is required.")

        if not InputValidator(pack_id).is_valid():
            raise serializers.ValidationError("pack_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        audio_file = AudioFiles.objects.prefetch_related("packs").filter(pk=audio_file_id,
                                                                         status=FileStatus.APPROVED.value).first()

        if not audio_file:
            raise serializers.ValidationError("audio file not found.")

        pack = audio_file.packs.first()

        if pack.id != pack_id and pack.submissions().first().status != SubmissionStatus.APPROVED.value:
            raise serializers.ValidationError("audio file not found.")

        user = self.context.get("user")

        collection = user.collections.filter(pk=collection_id, name=collection_name).first()

        if not collection:
            raise serializers.ValidationError("collection not found")

        attrs["collection"] = collection
        attrs["audio_file"] = audio_file
        attrs["pack"] = pack
        return attrs

    def create(self, validated_data):
        return CollectionFiles.objects.get_or_create(**validated_data)


class CollectionRemoveSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField(
        error_messages={"required": "collection_id is required", "blank": "collection_id cannot be blank"}
    )
    collection_name = serializers.CharField(
        error_messages={"required": "collection_name is required", "blank": "collection_name cannot be blank"}
    )
    pack_id = serializers.IntegerField(
        error_messages={"required": "pack_id is required", "blank": "pack_id cannot be blank"}
    )
    audio_file_id = serializers.IntegerField(
        error_messages={"required": "audio_file_id is required", "blank": "audio_file_id cannot be blank"}
    )

    class Meta:
        fields = ("collection_id", "collection_name", "pack_id", "audio_file_id")

    def validate(self, attrs):
        collection_id = attrs.pop("collection_id")
        collection_name = attrs.pop("collection_name")
        pack_id = attrs.pop("pack_id")
        audio_file_id = attrs.pop("audio_file_id")

        if not InputValidator(collection_name).is_valid():
            raise serializers.ValidationError("collection_name is required.")

        if not InputValidator(collection_id).is_valid():
            raise serializers.ValidationError("collection_id is required.")

        if not InputValidator(pack_id).is_valid():
            raise serializers.ValidationError("pack_id is required.")

        if not InputValidator(audio_file_id).is_valid():
            raise serializers.ValidationError("audio_file_id is required.")

        collection_file = CollectionFiles.objects.filter(collection__id=collection_id, audio_file__id=audio_file_id,
                                                         pack__id=pack_id).first()

        if not collection_file:
            raise serializers.ValidationError("file not found in given collection")

        collection_file.delete()

        return attrs


class ViewCollectionsFilesSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField(source="collection.id")
    pack_id = serializers.IntegerField(source="pack.id")
    audio_file_id = serializers.IntegerField(source="audio_file.id")
    file = serializers.FileField(source="audio_file.file.file")
    file_name = serializers.CharField(source="audio_file.file.file_name")
    pack_name = serializers.CharField(source="pack.title")
    artist = serializers.SerializerMethodField(method_name="get_artist")
    artwork = serializers.FileField(source="pack.artwork")
    created_at = serializers.SerializerMethodField(method_name="get_created_at")

    class Meta:
        fields = ("collection_id", "pack_id", "audio_file_id", "file", "file_name", "pack_name", "artist", "artwork",
                  "created_at")

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
