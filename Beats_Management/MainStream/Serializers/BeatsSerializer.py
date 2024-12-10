from rest_framework import serializers


class BeatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    artist = serializers.SerializerMethodField(method_name="get_artist")
    title = serializers.CharField(source="beat.title")
    beats_artwork = serializers.ImageField(source="beat.beats_artwork")

    class Meta:
        fields = ("id", "artist", "title", "beats_artwork")

    @staticmethod
    def get_artist(obj):
        if obj.supplier.is_admin:
            return obj.supplier.get_user_details().name
        if obj.supplier.is_supplier:
            return obj.supplier.get_user_details().artist.name


class BeatsAudioFileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    file = serializers.FileField(source="file.file")
    file_name = serializers.CharField(source="file.file_name")
    file_size = serializers.CharField(source="file.file_size")
    genre = serializers.CharField(source="genre.name")
    sub_genre = serializers.CharField(source="sub_genre.name")
    instrument = serializers.CharField(source="instrument.name")
    sub_instrument = serializers.CharField(source="sub_instrument.name")
    mood = serializers.CharField(source="mood.name")
    bpm_start_value = serializers.CharField(source="bpm.start_value")
    bpm_end_value = serializers.CharField(source="bpm.end_value")
    bpm_type = serializers.CharField(source="bpm.bpm_type")
    key = serializers.CharField(source="key.key")
    key_scale = serializers.CharField(source="key.key_scale")
    key_type = serializers.CharField(source="key.key_type")
    beat_type = serializers.CharField()
    source = serializers.CharField()

    class Meta:
        fields = ("id", "file", "file_name", "file_size", "genre", "sub_genre", "instrument", "sub_instrument", "mood",
                  "bpm_start_value", "bpm_end_value", "bpm_type", "key", "key_scale", "key_type", "beat_type", "source")


class BeatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    artist = serializers.SerializerMethodField(method_name="get_artist")
    title = serializers.CharField(source="beat.title")
    description = serializers.CharField(source="beat.description")
    genre = serializers.CharField(source="beat.genre.name")
    sub_genre = serializers.CharField(source="beat.sub_genre.name")
    mood = serializers.SerializerMethodField(method_name="get_mood")
    beats_artwork = serializers.ImageField(source="beat.beats_artwork")
    # demo_file = serializers.SerializerMethodField(method_name="get_demo_file")
    audio_files = serializers.SerializerMethodField(method_name="get_audio_files")
    files_count = serializers.IntegerField()

    class Meta:
        fields = (
            "id", "artist", "title", "description", "genre", "sub_genre", "mood", "beats_artwork", "audio_files",
            "files_count"
        )

    @staticmethod
    def get_mood(obj):
        return [mood.name for mood in obj.beat.mood.all()]

    @staticmethod
    def get_demo_file(obj):
        return BeatsAudioFileSerializer(obj.beat.demo_file).data

    @staticmethod
    def get_audio_files(obj):
        audio_files = obj.beat.audio_files.all()
        return BeatsAudioFileSerializer(audio_files, many=True).data

    @staticmethod
    def get_artist(obj):
        if obj.supplier.is_admin:
            return obj.supplier.get_user_details().name
        if obj.supplier.is_supplier:
            return obj.supplier.get_user_details().artist.name
