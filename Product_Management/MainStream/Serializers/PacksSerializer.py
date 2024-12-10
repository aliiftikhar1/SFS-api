from rest_framework import serializers


class PacksSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    artist = serializers.SerializerMethodField(method_name="get_artist")
    title = serializers.CharField(source="pack.title")
    artwork = serializers.ImageField(source="pack.artwork")

    class Meta:
        fields = ("id", "artist", "title", "artwork")

    @staticmethod
    def get_artist(obj):
        if obj.supplier.is_admin:
            return obj.supplier.get_user_details().name
        if obj.supplier.is_supplier:
            return obj.supplier.get_user_details().artist.name


class AudioFileSerializer(serializers.Serializer):
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
    type = serializers.CharField()
    source = serializers.CharField()

    class Meta:
        fields = ("id", "file", "file_name", "file_size", "genre", "sub_genre", "instrument", "sub_instrument", "mood",
                  "bpm_start_value", "bpm_end_value", "bpm_type", "key", "key_scale", "key_type", "type", "source")


class PackSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    artist = serializers.SerializerMethodField(method_name="get_artist")
    title = serializers.CharField(source="pack.title")
    description = serializers.CharField(source="pack.description")
    genre = serializers.CharField(source="pack.genre.name")
    sub_genre = serializers.CharField(source="pack.sub_genre.name")
    mood = serializers.SerializerMethodField(method_name="get_mood")
    artwork = serializers.ImageField(source="pack.artwork")
    # demo_file = serializers.SerializerMethodField(method_name="get_demo_file")
    audio_files = serializers.SerializerMethodField(method_name="get_audio_files")
    files_count = serializers.IntegerField()

    class Meta:
        fields = (
            "id", "artist", "title", "description", "genre", "sub_genre", "mood", "artwork", "audio_files",
            "files_count"
        )

    @staticmethod
    def get_mood(obj):
        return [mood.name for mood in obj.pack.mood.all()]

    @staticmethod
    def get_demo_file(obj):
        return AudioFileSerializer(obj.pack.demo_file).data

    @staticmethod
    def get_audio_files(obj):
        audio_files = obj.pack.audio_files.all()
        return AudioFileSerializer(audio_files, many=True).data

    @staticmethod
    def get_artist(obj):
        if obj.supplier.is_admin:
            return obj.supplier.get_user_details().name
        if obj.supplier.is_supplier:
            return obj.supplier.get_user_details().artist.name
