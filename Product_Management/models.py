from django.db import models

from User_Management.models import User, DateTimeModel
from Utilities.Enums import TypeTypes
from Utilities.Enums.BPMTypes import BPMTypes
from Utilities.Enums.FileStatus import FileStatus
from Utilities.Enums.KeyTypes import KeyTypes, KeyScaleTypes, FlatKeys, SharpKeys
from Utilities.Enums.PackTypes import PackTypes
from Utilities.Enums.SourceTypes import SourceTypes
from Utilities.Enums.SubmissionStatus import SubmissionStatus


class Mood(DateTimeModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class Genre(DateTimeModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class SubGenre(DateTimeModel):
    name = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name="sub_genre")


class Plugin(DateTimeModel):
    name = models.CharField(max_length=255)
    extension = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class Instrument(DateTimeModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class SubInstrument(DateTimeModel):
    name = models.CharField(max_length=255)
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="sub_instrument"
    )


class BPM(DateTimeModel):
    start_value = models.CharField(max_length=10)
    end_value = models.CharField(max_length=10)
    bpm_type = models.CharField(max_length=25, choices=BPMTypes.choices)


class Key(DateTimeModel):
    key = models.CharField(max_length=10, choices=SharpKeys.choices + FlatKeys.choices)
    key_scale = models.CharField(max_length=10, choices=KeyScaleTypes.choices)
    key_type = models.CharField(max_length=25, choices=KeyTypes.choices)


class File(DateTimeModel):
    file = models.FileField(
        upload_to="audio-files/", max_length=1000, default=None, null=True, blank=True
    )
    file_name = models.CharField(max_length=1000)
    file_size = models.CharField(max_length=50)


class AudioFiles(DateTimeModel):
    file = models.ForeignKey(
        File,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    sub_genre = models.ForeignKey(
        SubGenre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    sub_instrument = models.ForeignKey(
        SubInstrument,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    mood = models.ForeignKey(
        Mood,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    bpm = models.ForeignKey(
        BPM,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    key = models.ForeignKey(
        Key,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files"
    )
    likes_count = models.IntegerField(default=0)
    downloads_count = models.IntegerField(default=0)
    type = models.CharField(max_length=25, choices=TypeTypes.choices)
    source = models.CharField(max_length=25, choices=SourceTypes.choices)
    message = models.CharField(max_length=1000, default=None, null=True, blank=True)
    status = models.CharField(max_length=25, choices=FileStatus.choices, default=FileStatus.UPLOADED.value)


class Pack(DateTimeModel):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500, default="")
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="packs",
    )
    sub_genre = models.ForeignKey(
        SubGenre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="packs",
    )
    mood = models.ManyToManyField(
        Mood,
        blank=True,
        related_name="packs",
    )
    demo_file = models.OneToOneField(
        AudioFiles,
        on_delete=models.SET_NULL,
        null=True,
        related_name="demo",
    )
    artwork = models.ImageField(
        upload_to="artworks/", max_length=1000, default=None, null=True, blank=True
    )
    audio_files = models.ManyToManyField(
        AudioFiles,
        blank=True,
        related_name="packs",
    )
    downloads_count = models.IntegerField(default=0)


class PackSubmissions(DateTimeModel):
    pack = models.ForeignKey(
        Pack,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="submissions",
    )
    supplier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="packs_submissions",
    )
    approval_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="packs_review",
    )
    pack_type = models.CharField(max_length=25, choices=PackTypes.choices, default=PackTypes.SAMPLE.value)
    status = models.CharField(max_length=25, choices=SubmissionStatus.choices, default=SubmissionStatus.UPLOADED.value)


class Downloads(DateTimeModel):
    pack = models.ForeignKey(
        Pack,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="downloads",
    )
    member = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="downloads",
    )


class FileDownloads(DateTimeModel):
    download = models.ForeignKey(
        Downloads,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="files",
    )
    audio_file = models.ForeignKey(
        AudioFiles,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="downloads",
    )


class Likes(DateTimeModel):
    pack = models.ForeignKey(
        Pack,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="likes",
    )
    file = models.ForeignKey(
        AudioFiles,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="like",
    )
    member = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="likes",
    )


class Collections(DateTimeModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    member = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="collections",
    )


class CollectionFiles(DateTimeModel):
    pack = models.ForeignKey(
        Pack,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="collection_files",
    )
    audio_file = models.ForeignKey(
        AudioFiles,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="collection_files",
    )
    collection = models.ForeignKey(
        Collections,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="collection_files",
    )
