from rest_framework import serializers

from Product_Management.models import PackSubmissions, AudioFiles


class AudioFileSerializer(serializers.Serializer):
    file_id = serializers.IntegerField(read_only=True, source="file.id")
    file = serializers.FileField(source="file.file")
    file_name = serializers.CharField(source="file.file_name")
    file_size = serializers.CharField(source="file.file_size")
    file_genre = serializers.SerializerMethodField(method_name="get_file_genre", source="genre")
    file_instrument = serializers.SerializerMethodField(method_name="get_file_instrument", source="instrument")
    file_mood = serializers.SerializerMethodField(method_name="get_file_mood", source="mood")
    file_bpm_start_value = serializers.CharField(source="bpm.start_value")
    file_bpm_end_value = serializers.CharField(source="bpm.end_value")
    file_bpm_type = serializers.CharField(source="bpm.bpm_type")
    file_key = serializers.CharField(source="key.key")
    file_key_scale = serializers.CharField(source="key.key_scale")
    file_key_type = serializers.CharField(source="key.key_type")
    file_type = serializers.CharField(source="type")
    file_source = serializers.CharField(source="source")
    file_revision_message = serializers.CharField(source="message")
    file_status = serializers.CharField(source="status")

    @staticmethod
    def get_file_mood(obj):
        mood = obj.mood
        return {'id': mood.id, 'name': mood.name}

    @staticmethod
    def get_file_genre(obj):
        genre = obj.genre
        sub_genre = obj.sub_genre
        return {'id': genre.id, 'name': genre.name,
                'sub_genre': {"id": sub_genre.id, "name": sub_genre.name}}

    @staticmethod
    def get_file_instrument(obj):
        instrument = obj.instrument
        sub_instrument = obj.sub_instrument
        return {'id': instrument.id, 'name': instrument.name,
                'sub_instrument': {"id": sub_instrument.id, "name": sub_instrument.name}}

    class Meta:
        model = AudioFiles
        fields = (
            "file_id", "file", "file_name", "file_size", "file_genre", "file_sub_genre", "file_instrument",
            "file_sub_instrument",
            "file_mood", "file_bpm_start_value", "file_bpm_end_value", "file_bpm_type", "file_key", "file_key_scale",
            "file_key_type", "file_type", "fle_source", "file_type", "file_source", "file_status"
        )


class ViewPacksSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(source="id", read_only=True)
    pack_id = serializers.IntegerField(source="pack.id", read_only=True)
    pack_title = serializers.CharField(source="pack.title")
    pack_genre = serializers.SerializerMethodField(method_name="get_pack_genre", source="pack.genre")
    pack_moods = serializers.SerializerMethodField(method_name="get_pack_moods")
    pack_description = serializers.CharField(source="pack.description")
    pack_demo_file = AudioFileSerializer(source="pack.demo_file")
    pack_artwork_file = serializers.FileField(source="pack.artwork")
    pack_audio_files = AudioFileSerializer(many=True, source="pack.audio_files")
    pack_supplier = serializers.SerializerMethodField(method_name="get_pack_supplier", source="supplier")
    pack_approval_person = serializers.SerializerMethodField(method_name="get_pack_approval_person",
                                                             source="approval_person")
    pack_type = serializers.CharField()
    status = serializers.CharField()

    @staticmethod
    def get_pack_moods(obj):
        moods = obj.pack.mood.all()
        return [{'id': mood.id, 'name': mood.name} for mood in moods]

    @staticmethod
    def get_pack_genre(obj):
        genre = obj.pack.genre
        sub_genre = obj.pack.sub_genre
        return {'id': genre.id, 'name': genre.name,
                'sub_genre': {"id": sub_genre.id, "name": sub_genre.name}}

    @staticmethod
    def get_pack_supplier(obj):
        supplier = obj.supplier
        details = supplier.get_user_details()
        if supplier.is_admin:
            return {'id': supplier.id, 'name': details.name}
        return {'id': supplier.id, 'name': details.first_name}

    @staticmethod
    def get_pack_approval_person(obj):
        staff = obj.approval_person
        details = staff.get_user_details()
        return {'id': staff.id, 'name': details.name}

    class Meta:
        model = PackSubmissions
        fields = (
            "request_id", "pack_id", "pack_title", "pack_genre", "pack_sub_genre", "pack_moods", "pack_description",
            "pack_artwork", "pack_audio_files", "pack_demo_file", "pack_demo_file_name", "pack_demo_file_size",
            "pack_supplier", "pack_type", "status", "approval_person"
        )
