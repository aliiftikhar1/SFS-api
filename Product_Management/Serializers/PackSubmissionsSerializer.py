import os

from django.db import transaction
from rest_framework import serializers

from Product_Management.Serializers.FindApprovalPerson import find_approval_person
from Product_Management.models import Genre, File, Pack, PackSubmissions, Mood, Instrument, Key, BPM, \
    AudioFiles
from Utilities.Enums import BPMTypes, FlatKeys, SharpKeys, KeyScaleTypes, KeyTypes, PackTypes, SourceTypes, \
    SubmissionStatus, TypeTypes, FileStatus, Boolean
from Utilities.Validators import InputValidator


def validate_wav_file(file):
    ext = os.path.splitext(file.name)[1]
    # TODO Uncomment audio file type
    # if ext.lower() != '.wav':
    #     raise serializers.ValidationError("Only .wav extension files are allowed for in audio files.")
    return file


def validate_image_file(file):
    content_type = file.content_type
    # TODO Uncomment artwork file type
    # if 'image' not in content_type:
    #     raise serializers.ValidationError("Only extension files are allowed for artwork.")
    return file


def validate_audio_file_data(attrs):
    file = attrs.get("file")
    file_name = attrs.get("file_name")
    file_size = attrs.get("file_size")
    file_genre = attrs.get("file_genre")
    file_sub_genre = attrs.get("file_sub_genre")
    file_instrument = attrs.get("file_instrument")
    file_sub_instrument = attrs.get("file_sub_instrument")
    file_mood = attrs.get("file_mood")
    file_bpm_start_value = attrs.get("file_bpm_start_value")
    file_bpm_end_value = attrs.get("file_bpm_end_value")
    file_bpm_type = attrs.get("file_bpm_type")
    file_key = attrs.get("file_key")
    file_key_scale = attrs.get("file_key_scale")
    file_key_type = attrs.get("file_key_type")
    file_type = attrs.get("file_type")
    file_source = attrs.get("file_source")

    if not file:
        raise serializers.ValidationError("file is required")

    if not InputValidator(file_name).is_valid():
        raise serializers.ValidationError("file_name is required")

    if not InputValidator(file_size).is_valid():
        raise serializers.ValidationError("file_size is required")

    if not InputValidator(file_genre).is_valid():
        raise serializers.ValidationError("file_genre is required")

    if not InputValidator(file_sub_genre).is_valid():
        raise serializers.ValidationError("file_sub_genre is required")

    genre = Genre.objects.prefetch_related("sub_genre").filter(name=file_genre).first()

    if not genre:
        raise serializers.ValidationError("invalid genre")

    sub_genre = genre.sub_genre.filter(name=file_sub_genre).first()

    if not sub_genre:
        raise serializers.ValidationError(f"invalid sub_genre under {genre.name}")

    if not InputValidator(file_instrument).is_valid():
        raise serializers.ValidationError("file_instrument is required")

    if not InputValidator(file_sub_instrument).is_valid():
        raise serializers.ValidationError("file_sub_instrument is required")

    instrument = Instrument.objects.prefetch_related("sub_instrument").filter(name=file_instrument).first()

    if not instrument:
        raise serializers.ValidationError("invalid instrument")

    sub_instrument = instrument.sub_instrument.filter(name=file_sub_instrument).first()

    if not sub_instrument:
        raise serializers.ValidationError(f"invalid sub_instrument under {instrument.name}")

    if not InputValidator(file_mood).is_valid():
        raise serializers.ValidationError("file_mood is required")

    mood = Mood.objects.filter(name=file_mood).first()

    if not mood:
        raise serializers.ValidationError("invalid mood")

    if not InputValidator(file_bpm_start_value).is_valid():
        raise serializers.ValidationError("file_bpm_start_value is required")

    if not InputValidator(file_bpm_end_value).is_valid():
        raise serializers.ValidationError("file_bpm_end_value is required")

    if not InputValidator(file_bpm_type).is_valid():
        raise serializers.ValidationError("file_bpm_type is required")

    if not InputValidator(file_bpm_type).is_valid_option(BPMTypes.list()):
        raise serializers.ValidationError("Invalid file_bpm_type")

    if (not file_bpm_start_value.isnumeric()) or (not file_bpm_end_value.isnumeric()):
        raise serializers.ValidationError("file_bpm_start_value and file_bpm_end_value should be numerical values")

    if int(file_bpm_start_value) > int(file_bpm_end_value):
        raise serializers.ValidationError("file_bpm_start_value should be less than file_bpm_end_value")

    if int(file_bpm_start_value) < 0 or int(file_bpm_end_value) < 0:
        raise serializers.ValidationError("file_bpm_start_value or file_bpm_end_value cannot be zero")

    if file_bpm_type == BPMTypes.EXACT.value and file_bpm_start_value != file_bpm_end_value:
        raise serializers.ValidationError(
            "file_bpm_start_value should be equal to file_bpm_end_value in exact range case")

    if not InputValidator(file_key).is_valid():
        raise serializers.ValidationError("file_key is required")

    if not InputValidator(file_key_scale).is_valid():
        raise serializers.ValidationError("file_key_scale is required")

    if not InputValidator(file_key_type).is_valid():
        raise serializers.ValidationError("file_key_type is required")

    if not InputValidator(file_key).is_valid_option([*FlatKeys.list(), *SharpKeys.list()]):
        raise serializers.ValidationError("Invalid file_key")

    if not InputValidator(file_key_scale).is_valid_option(KeyScaleTypes.list()):
        raise serializers.ValidationError("Invalid file_key_scale")

    if not InputValidator(file_key_type).is_valid_option(KeyTypes.list()):
        raise serializers.ValidationError("Invalid file_key_type")

    if file_key_type == KeyTypes.FLAT.value:
        if not InputValidator(file_key).is_valid_option(FlatKeys.list()):
            raise serializers.ValidationError("given key is not flat")

    if file_key_type == KeyTypes.SHARP.value:
        if not InputValidator(file_key).is_valid_option(SharpKeys.list()):
            raise serializers.ValidationError("given key is not sharp")

    if not InputValidator(file_type).is_valid():
        raise serializers.ValidationError("file_type is required")

    if not InputValidator(file_type).is_valid_option(TypeTypes.list()):
        raise serializers.ValidationError("Invalid file_type")

    if not InputValidator(file_source).is_valid():
        raise serializers.ValidationError("file_source is required")

    if not InputValidator(file_source).is_valid_option(SourceTypes.list()):
        raise serializers.ValidationError("Invalid file_source")

    attrs['instrument'] = instrument
    attrs['sub_instrument'] = sub_instrument
    attrs['genre'] = genre
    attrs['sub_genre'] = sub_genre
    attrs['mood'] = mood
    return attrs


class AudioFileSerializer(serializers.Serializer):
    file = serializers.FileField(
        error_messages={
            "required": "file is required",
            "blank": "file cannot be blank"
        }
    )
    file_name = serializers.CharField(
        error_messages={
            "required": "file_name is required",
            "blank": "file_name cannot be blank"
        }
    )
    file_size = serializers.CharField(
        error_messages={
            "required": "file_size is required",
            "blank": "file_size cannot be blank"
        }
    )
    file_genre = serializers.CharField(
        error_messages={
            "required": "file_genre is required",
            "blank": "file_genre cannot be blank",
        }
    )
    file_sub_genre = serializers.CharField(
        error_messages={
            "required": "file_sub_genre is required",
            "blank": "file_sub_genre cannot be blank",
        }
    )
    file_instrument = serializers.CharField(
        error_messages={
            "required": "file_instrument is required",
            "blank": "file_instrument cannot be blank",
        }
    )
    file_sub_instrument = serializers.CharField(
        error_messages={
            "required": "file_sub_instrument is required",
            "blank": "file_sub_instrument cannot be blank",
        }
    )
    file_mood = serializers.CharField(
        error_messages={
            "required": "file_mood is required",
            "blank": "file_mood cannot be blank",
        }
    )
    file_bpm_start_value = serializers.CharField(
        error_messages={
            "required": "file_bpm_start_value is required",
            "blank": "file_bpm_start_value cannot be blank"
        }
    )
    file_bpm_end_value = serializers.CharField(
        error_messages={
            "required": "file_bpm_end_value is required",
            "blank": "file_bpm_end_value cannot be blank"
        }
    )
    file_bpm_type = serializers.CharField(
        error_messages={
            "required": "file_bpm_type is required",
            "blank": "file_bpm_type cannot be blank"
        }
    )
    file_key = serializers.CharField(
        error_messages={
            "required": "file_key is required",
            "blank": "file_key cannot be blank"
        }
    )
    file_key_scale = serializers.CharField(
        error_messages={
            "required": "file_key_scale is required",
            "blank": "file_key_scale cannot be blank"
        }
    )
    file_key_type = serializers.CharField(
        error_messages={
            "required": "file_key_type is required",
            "blank": "file_key_type cannot be blank"
        }
    )
    file_type = serializers.CharField(
        error_messages={
            "required": "file_type is required",
            "blank": "file_type cannot be blank",
        }
    )
    file_source = serializers.CharField(
        error_messages={
            "required": "file_source is required",
            "blank": "file_source cannot be blank",
        }
    )

    @staticmethod
    def validate_file(value):
        return validate_wav_file(value)

    def validate(self, attrs):
        return validate_audio_file_data(attrs)

    def create(self, validated_data):
        file = validated_data.get("file")
        file_name = validated_data.get("file_name")
        file_size = validated_data.get("file_size")
        file_bpm_type = validated_data.get("file_bpm_type")
        file_bpm_end_value = validated_data.get("file_bpm_end_value")
        file_bpm_start_value = validated_data.get("file_bpm_start_value")
        file_key = validated_data.get("file_key")
        file_key_scale = validated_data.get("file_key_scale")
        file_key_type = validated_data.get("file_key_type")
        file_type = validated_data.get("file_type")
        file_source = validated_data.get("file_source")

        file_genre = validated_data.get("genre")
        file_sub_genre = validated_data.get("sub_genre")
        file_instrument = validated_data.get("instrument")
        file_sub_instrument = validated_data.get("sub_instrument")
        file_mood = validated_data.get("mood")

        with transaction.atomic():
            file = File.objects.create(file=file, file_name=file_name, file_size=file_size)
            file_key = Key.objects.create(key=file_key, key_scale=file_key_scale, key_type=file_key_type)
            file_bpm = BPM.objects.create(start_value=file_bpm_start_value, end_value=file_bpm_end_value,
                                          bpm_type=file_bpm_type)

            audio_file = AudioFiles.objects.create(file=file, genre=file_genre, sub_genre=file_sub_genre,
                                                   instrument=file_instrument, sub_instrument=file_sub_instrument,
                                                   mood=file_mood, bpm=file_bpm, key=file_key, type=file_type,
                                                   source=file_source)
            return audio_file


class DemoFileSerializer(AudioFileSerializer):
    class Meta:
        ref_name = "demo_file"


class AudioFilesSerializer(AudioFileSerializer):
    class Meta:
        ref_name = "audio_files"


class PackSubmissionsSerializer(serializers.Serializer):
    pack_title = serializers.CharField(
        error_messages={
            "required": "pack_title is required",
            "blank": "pack_title cannot be blank",
        }
    )
    pack_genre = serializers.CharField(
        error_messages={
            "required": "pack_genre is required",
            "blank": "pack_genre cannot be blank",
        }
    )
    pack_sub_genre = serializers.CharField(
        error_messages={
            "required": "pack_sub_genre is required",
            "blank": "pack_sub_genre cannot be blank",
        }
    )
    pack_moods = serializers.ListField(
        error_messages={
            "required": "pack_moods are required"
        },
        child=serializers.CharField(
            error_messages={
                "required": "pack_mood is required",
                "blank": "pack_mood cannot be blank",
            }
        )
    )
    pack_description = serializers.CharField(
        error_messages={
            "required": "pack_description is required",
            "blank": "pack_description cannot be blank",
        }
    )
    pack_demo = DemoFileSerializer()
    pack_artwork_file = serializers.FileField(
        error_messages={
            "required": "pack_artwork_file is required",
            "blank": "pack_artwork_file cannot be blank"
        }
    )
    pack_audio_files = serializers.ListField(
        error_messages={
            "required": "pack_audio_files is required",
            "blank": "pack_audio_files cannot be blank"
        },
        child=AudioFilesSerializer()
    )
    pack_type = serializers.CharField(
        error_messages={
            "required": "pack_type is required",
            "blank": "pack_type cannot be blank"
        }
    )

    @staticmethod
    def validate_pack_artwork_file(value):
        return validate_image_file(value)

    def validate(self, attrs):
        pack_title = attrs.get("pack_title")
        pack_genre = attrs.get("pack_genre")
        pack_sub_genre = attrs.get("pack_sub_genre")
        pack_moods = attrs.get("pack_moods")
        pack_description = attrs.get("pack_description")
        pack_demo = attrs.get("pack_demo")
        pack_artwork_file = attrs.get("pack_artwork_file")
        pack_audio_files = attrs.get("pack_audio_files")
        pack_type = attrs.get("pack_type")

        if not InputValidator(pack_title).is_valid():
            raise serializers.ValidationError("pack_title is required")

        pack = PackSubmissions.objects.select_related("pack").filter(pack_type=pack_type,
                                                                     pack__title=pack_title).first()

        if pack:
            raise serializers.ValidationError("pack_title already exists")

        if not InputValidator(pack_description).is_valid():
            raise serializers.ValidationError("pack_description is required")

        if not InputValidator(pack_type).is_valid():
            raise serializers.ValidationError("pack_type is required")

        if not InputValidator(pack_type).is_valid_option(PackTypes.list()):
            raise serializers.ValidationError("invalid pack_type")

        if pack_demo is None:
            raise serializers.ValidationError("pack_demo is required")

        if not pack_artwork_file:
            raise serializers.ValidationError("pack_artwork_file is required")

        if not InputValidator(pack_moods).has_valid_length(3, 3):
            raise serializers.ValidationError("pack_mood must be 3")

        moods = Mood.objects.filter(name__in=pack_moods)

        if len(moods) < len(pack_moods):
            raise serializers.ValidationError("provide valid moods")

        # TODO Uncomment audio file limit
        # if not InputValidator(pack_audio_files).has_valid_length(min_length=100):
        #     raise serializers.ValidationError("audio_files must be at least 100")

        genre = Genre.objects.prefetch_related("sub_genre").filter(name=pack_genre).first()

        if genre is None:
            raise serializers.ValidationError("pack_genre does not exist")

        sub_genre = genre.sub_genre.filter(name=pack_sub_genre).first()

        if sub_genre is None:
            raise serializers.ValidationError("pack_sub_genre does not exist")

        with transaction.atomic():
            audio_files_serializer = AudioFileSerializer(data=pack_audio_files, many=True)
            audio_files_serializer.is_valid()
            if audio_files_serializer.errors:
                raise serializers.ValidationError(audio_files_serializer.errors)
            audio_files = audio_files_serializer.save()

            pack_demo_serializer = AudioFileSerializer(data=pack_demo)
            pack_demo_serializer.is_valid()
            if pack_demo_serializer.errors:
                raise serializers.ValidationError(pack_demo_serializer.errors)
            pack_demo = pack_demo_serializer.save()

        attrs["moods"] = moods
        attrs["genre"] = genre
        attrs["sub_genre"] = sub_genre
        attrs["pack_demo"] = pack_demo
        attrs["audio_files"] = audio_files
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            pack_title = validated_data.get("pack_title")
            pack_description = validated_data.get("pack_description")
            pack_demo = validated_data.get("pack_demo")
            pack_type = validated_data.get("pack_type")
            pack_artwork_file = validated_data.get("pack_artwork_file")

            moods = validated_data.get("moods")
            pack_genre = validated_data.get("genre")
            audio_files = validated_data.get("audio_files")
            pack_sub_genre = validated_data.get("sub_genre")

            supplier = self.context.get("supplier")

            approval_person = find_approval_person()

            pack = Pack.objects.create(title=pack_title, description=pack_description, genre=pack_genre,
                                       sub_genre=pack_sub_genre, demo_file=pack_demo,
                                       artwork=pack_artwork_file)
            pack.mood.set(moods)
            pack.audio_files.set(audio_files)
            pack.save()

            submission = PackSubmissions.objects.create(supplier=supplier, pack=pack, approval_person=approval_person,
                                                        pack_type=pack_type, status=SubmissionStatus.UPLOADED)
            return submission


class RevisedAudioFileSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(
        error_messages={
            "required": "request_id is required",
            "blank": "request_id cannot be blank"
        }
    )
    pack_id = serializers.IntegerField(
        error_messages={
            "required": "pack_id is required",
            "blank": "pack_id cannot be blank"
        }
    )
    pack_type = serializers.CharField(
        error_messages={
            "required": "pack_type is required",
            "blank": "pack_type cannot be blank"
        }
    )
    file_id = serializers.IntegerField(
        error_messages={
            "required": "file_id is required",
            "blank": "file_id cannot be blank"
        }
    )
    file = serializers.FileField(
        error_messages={
            "required": "file is required",
            "blank": "file cannot be blank"
        }
    )
    file_name = serializers.CharField(
        error_messages={
            "required": "file_name is required",
            "blank": "file_name cannot be blank"
        }
    )
    file_size = serializers.CharField(
        error_messages={
            "required": "file_size is required",
            "blank": "file_size cannot be blank"
        }
    )
    file_genre = serializers.CharField(
        error_messages={
            "required": "file_genre is required",
            "blank": "file_genre cannot be blank",
        }
    )
    file_sub_genre = serializers.CharField(
        error_messages={
            "required": "file_sub_genre is required",
            "blank": "file_sub_genre cannot be blank",
        }
    )
    file_instrument = serializers.CharField(
        error_messages={
            "required": "file_instrument is required",
            "blank": "file_instrument cannot be blank",
        }
    )
    file_sub_instrument = serializers.CharField(
        error_messages={
            "required": "file_sub_instrument is required",
            "blank": "file_sub_instrument cannot be blank",
        }
    )
    file_mood = serializers.CharField(
        error_messages={
            "required": "file_mood is required",
            "blank": "file_mood cannot be blank",
        }
    )
    file_bpm_start_value = serializers.CharField(
        error_messages={
            "required": "file_bpm_start_value is required",
            "blank": "file_bpm_start_value cannot be blank"
        }
    )
    file_bpm_end_value = serializers.CharField(
        error_messages={
            "required": "file_bpm_end_value is required",
            "blank": "file_bpm_end_value cannot be blank"
        }
    )
    file_bpm_type = serializers.CharField(
        error_messages={
            "required": "file_bpm_type is required",
            "blank": "file_bpm_type cannot be blank"
        }
    )
    file_key = serializers.CharField(
        error_messages={
            "required": "file_key is required",
            "blank": "file_key cannot be blank"
        }
    )
    file_key_scale = serializers.CharField(
        error_messages={
            "required": "file_key_scale is required",
            "blank": "file_key_scale cannot be blank"
        }
    )
    file_key_type = serializers.CharField(
        error_messages={
            "required": "file_key_type is required",
            "blank": "file_key_type cannot be blank"
        }
    )
    file_type = serializers.CharField(
        error_messages={
            "required": "file_type is required",
            "blank": "file_type cannot be blank",
        }
    )
    file_source = serializers.CharField(
        error_messages={
            "required": "file_source is required",
            "blank": "file_source cannot be blank",
        }
    )
    is_demo_file = serializers.BooleanField(
        default=False
    )

    @staticmethod
    def validate_file(value):
        return validate_wav_file(value)

    def validate(self, attrs):
        user = self.context.get("user")
        request_id = attrs.get("request_id")
        pack_id = attrs.get("pack_id")
        file_id = attrs.get("file_id")
        file_genre = attrs.get("file_genre")
        file_sub_genre = attrs.get("file_sub_genre")
        file_instrument = attrs.get("file_instrument")
        file_sub_instrument = attrs.get("file_sub_instrument")
        file_mood = attrs.get("file_mood")
        pack_type = attrs.get("pack_type")
        is_demo_file = attrs.get("is_demo_file")

        mood = Mood.objects.filter(name=file_mood).first()

        if not mood:
            raise serializers.ValidationError("invalid mood")

        instrument = Instrument.objects.prefetch_related("sub_instrument").filter(name=file_instrument).first()

        if not instrument:
            raise serializers.ValidationError("invalid instrument")

        genre = Genre.objects.prefetch_related("sub_genre").filter(name=file_genre).first()

        if not genre:
            raise serializers.ValidationError("invalid genre")

        sub_instrument = instrument.sub_instrument.filter(name=file_sub_instrument).first()

        if not sub_instrument:
            raise serializers.ValidationError(f"invalid sub_instrument under {instrument.name}")

        sub_genre = genre.sub_genre.filter(name=file_sub_genre).first()

        if not sub_genre:
            raise serializers.ValidationError(f"invalid sub_genre under {genre.name}")

        submission = PackSubmissions.objects.select_related("pack", "pack__demo_file", "supplier").filter(
            id=request_id,
            pack__id=pack_id,
            supplier=user,
            pack_type=pack_type).first()

        if not InputValidator(submission.status).is_valid_option([SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
            raise serializers.ValidationError("cannot revise submission")

        if not submission:
            raise serializers.ValidationError("Pack submission does not exist")

        if Boolean.get_bool(is_demo_file):
            file = submission.pack.demo_file
            if file.id != file_id:
                raise serializers.ValidationError("Pack demo file does not exist")
        else:
            file = submission.pack.audio_files.select_related("file").filter(file__id=file_id).first()
            if not file:
                raise serializers.ValidationError("Pack demo file does not exist")

        attrs = validate_audio_file_data(attrs)

        attrs['submitted_file'] = file
        return attrs

    def create(self, validated_data):
        submitted_file = validated_data.get("submitted_file")
        file = validated_data.get("file")
        file_name = validated_data.get("file_name")
        file_size = validated_data.get("file_size")
        file_bpm_type = validated_data.get("file_bpm_type")
        file_bpm_end_value = validated_data.get("file_bpm_end_value")
        file_bpm_start_value = validated_data.get("file_bpm_start_value")
        file_key = validated_data.get("file_key")
        file_key_scale = validated_data.get("file_key_scale")
        file_key_type = validated_data.get("file_key_type")
        file_type = validated_data.get("file_type")
        file_source = validated_data.get("file_source")

        file_genre = validated_data.get("genre")
        file_sub_genre = validated_data.get("sub_genre")
        file_instrument = validated_data.get("instrument")
        file_sub_instrument = validated_data.get("sub_instrument")
        file_mood = validated_data.get("mood")

        with transaction.atomic():
            if submitted_file.key.key != file_key:
                submitted_file.key.key = file_key
            if submitted_file.key.key_scale != file_key_scale:
                submitted_file.key.key_scale = file_key_scale
            if submitted_file.key.key_type != file_key_type:
                submitted_file.key.key_type = file_key_type
            submitted_file.key.save()

            if submitted_file.bpm.bpm_type != file_bpm_type:
                submitted_file.bpm.bpm_type = file_bpm_type
            if submitted_file.bpm.start_value != file_bpm_start_value:
                submitted_file.bpm.start_value = file_bpm_start_value
            if submitted_file.bpm.end_value != file_bpm_end_value:
                submitted_file.bpm.end_value = file_bpm_end_value
            submitted_file.bpm.save()

            if submitted_file.file.file != file:
                submitted_file.file.file.delete()
                submitted_file.file.file = file
            if submitted_file.file.file_name != file_name:
                submitted_file.file.file_name = file_name
            if submitted_file.file.file_size != file_size:
                submitted_file.file.file_size = file_size
            submitted_file.file.save()

            if submitted_file.genre != file_genre:
                submitted_file.genre = file_genre

            if submitted_file.sub_genre != file_sub_genre:
                submitted_file.sub_genre = file_sub_genre

            if submitted_file.instrument != file_instrument:
                submitted_file.instrument = file_instrument

            if submitted_file.sub_instrument != file_sub_instrument:
                submitted_file.sub_instrument = file_sub_instrument

            if submitted_file.mood != file_mood:
                submitted_file.mood = file_mood

            if submitted_file.type != file_type:
                submitted_file.type = file_type

            if submitted_file.source != file_source:
                submitted_file.source = file_source

            submitted_file.status = FileStatus.REVISED
            submitted_file.save()
            return submitted_file
