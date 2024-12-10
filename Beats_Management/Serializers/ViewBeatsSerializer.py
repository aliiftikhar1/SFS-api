from rest_framework import serializers

from Beats_Management.models import BeatsSubmissions, BeatAudioFiles


class BeatAudioFileSerializer(serializers.Serializer):
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
    file_type = serializers.CharField(source="beat_type")
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
        model = BeatAudioFiles
        fields = (
            "file_id", "file", "file_name", "file_size", "file_genre", "file_sub_genre", "file_instrument",
            "file_sub_instrument",
            "file_mood", "file_bpm_start_value", "file_bpm_end_value", "file_bpm_type", "file_key", "file_key_scale",
            "file_key_type", "file_type", "file_source", "file_status"
        )


class ViewBeatsSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(source="id", read_only=True)
    beat_id = serializers.IntegerField(source="beat.id", read_only=True)
    beat_title = serializers.CharField(source="beat.title")
    beat_genre = serializers.SerializerMethodField(method_name="get_beat_genre", source="beat.genre")
    beat_moods = serializers.SerializerMethodField(method_name="get_beat_moods")
    beat_description = serializers.CharField(source="beat.description")
    beat_demo_file = BeatAudioFileSerializer(source="beat.demo_file")
    beat_artwork_file = serializers.FileField(source="beat.beats_artwork")
    beat_audio_files = BeatAudioFileSerializer(many=True, source="beat.audio_files")
    beat_supplier = serializers.SerializerMethodField(method_name="get_beat_supplier", source="supplier")
    beat_approval_person = serializers.SerializerMethodField(method_name="get_beat_approval_person",
                                                             source="approval_person")
    beat_type = serializers.CharField()
    status = serializers.CharField()

    @staticmethod
    def get_beat_moods(obj):
        moods = obj.beat.mood.all()
        return [{'id': mood.id, 'name': mood.name} for mood in moods]

    @staticmethod
    def get_beat_genre(obj):
        genre = obj.beat.genre
        sub_genre = obj.beat.sub_genre
        return {'id': genre.id, 'name': genre.name,
                'sub_genre': {"id": sub_genre.id, "name": sub_genre.name}}

    @staticmethod
    def get_beat_supplier(obj):
        supplier = obj.supplier
        details = supplier.get_user_details()
        if supplier.is_admin:
            return {'id': supplier.id, 'name': details.name}
        return {'id': supplier.id, 'name': details.first_name}

    @staticmethod
    def get_beat_approval_person(obj):
        staff = obj.approval_person
        details = staff.get_user_details()
        return {'id': staff.id, 'name': details.name}

    class Meta:
        model = BeatsSubmissions
        fields = (
            "request_id", "beat_id", "beat_title", "beat_genre", "beat_sub_genre", "beat_moods", "beat_description",
            "beat_artwork", "beat_audio_files", "beat_demo_file", "beat_demo_file_name", "beat_demo_file_size",
            "beat_supplier", "beat_type", "status", "approval_person"
        )
