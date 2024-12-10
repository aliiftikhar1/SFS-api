from django.db import models

from User_Management.models import User, DateTimeModel
from Utilities.Enums import TypeTypes
from Utilities.Enums.BPMTypes import BPMTypes
from Utilities.Enums.FileStatus import FileStatus
from Utilities.Enums.KeyTypes import KeyTypes, KeyScaleTypes, FlatKeys, SharpKeys
from Utilities.Enums.BeatTypes import BeatTypes
from Utilities.Enums.BeatFileTypes import BeatFileTypes
from Utilities.Enums.SourceTypes import SourceTypes
from Utilities.Enums.SubmissionStatus import SubmissionStatus


class BeatMood(DateTimeModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class BeatGenre(DateTimeModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class BeatSubGenre(DateTimeModel):
    name = models.CharField(max_length=255)
    genre = models.ForeignKey(BeatGenre, on_delete=models.CASCADE, related_name="sub_genre")


class BeatPlugin(DateTimeModel):
    name = models.CharField(max_length=255)
    extension = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class BeatInstrument(DateTimeModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class BeatSubInstrument(DateTimeModel):
    name = models.CharField(max_length=255)
    instrument = models.ForeignKey(
        BeatInstrument, on_delete=models.CASCADE, related_name="sub_instrument"
    )


class BeatBPM(DateTimeModel):
    start_value = models.CharField(max_length=10)
    end_value = models.CharField(max_length=10)
    bpm_type = models.CharField(max_length=25, choices=BPMTypes.choices)


class BeatKey(DateTimeModel):
    key = models.CharField(max_length=10, choices=SharpKeys.choices + FlatKeys.choices)
    key_scale = models.CharField(max_length=10, choices=KeyScaleTypes.choices)
    key_type = models.CharField(max_length=25, choices=KeyTypes.choices)


class BeatFile(DateTimeModel):
    file = models.FileField(
        upload_to="audio-beat-files/", max_length=1000, default=None, null=True, blank=True
    )
    file_name = models.CharField(max_length=1000)
    file_size = models.CharField(max_length=50)
    file_extension = models.CharField(max_length=10, choices=BeatFileTypes.choices , default=BeatFileTypes.mp3.value)
  
class BeatAudioFiles(DateTimeModel):
    file = models.ForeignKey(
        BeatFile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    genre = models.ForeignKey(
        BeatGenre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    sub_genre = models.ForeignKey(
        BeatSubGenre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    instrument = models.ForeignKey(
        BeatInstrument,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    sub_instrument = models.ForeignKey(
        BeatSubInstrument,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    mood = models.ForeignKey(
        BeatMood,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    bpm = models.ForeignKey(
        BeatBPM,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files",
    )
    key = models.ForeignKey(
        BeatKey,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audio_files"
    )
    likes_count = models.IntegerField(default=0)
    downloads_count = models.IntegerField(default=0)
    beat_type = models.CharField(max_length=25, choices=BeatTypes.choices)
    source = models.CharField(max_length=25, choices=SourceTypes.choices)
    message = models.CharField(max_length=1000, default=None, null=True, blank=True)
    status = models.CharField(max_length=25, choices=FileStatus.choices, default=FileStatus.UPLOADED.value)


class Beats(DateTimeModel):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500, default="")
    genre = models.ForeignKey(
        BeatGenre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beats",
    )
    sub_genre = models.ForeignKey(
        BeatSubGenre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beats",
    )
    mood = models.ManyToManyField(
        BeatMood,
        blank=True,
        related_name="beats",
    )
    demo_file = models.OneToOneField(
        BeatAudioFiles,
        on_delete=models.SET_NULL,
        null=True,
        related_name="demo",
    )
    beats_artwork = models.ImageField(
        upload_to="beats_artworks/", max_length=1000, default=None, null=True, blank=True
    )
    audio_files = models.ManyToManyField(
        BeatAudioFiles,
        blank=True,
        related_name="beats",
    )
    downloads_count = models.IntegerField(default=0)
    exclusive_price = models.IntegerField(default=0)


class BeatsSubmissions(DateTimeModel):
    beat = models.ForeignKey(
        Beats,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_submissions",
    )
    supplier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beats_submissions",
    )
    approval_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beats_review",
    )
    beat_type = models.CharField(max_length=25, choices=BeatTypes.choices, default=BeatTypes.BEAT.value)
    status = models.CharField(max_length=25, choices=SubmissionStatus.choices, default=SubmissionStatus.UPLOADED.value)


class BeatDownloads(DateTimeModel):
    beat = models.ForeignKey(
        Beats,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_downloads",
    )
    member = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_downloads",
    )


class BeatFileDownloads(DateTimeModel):
    download = models.ForeignKey(
        BeatDownloads,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_files",
    )
    audio_file = models.ForeignKey(
        BeatAudioFiles,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_downloads",
    )


class BeatLikes(DateTimeModel):
    beat = models.ForeignKey(
        Beats,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_likes",
    )
    file = models.ForeignKey(
        BeatAudioFiles,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_like",
    )
    member = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_likes",
    )


class BeatCollections(DateTimeModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    member = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_collections",
    )


class BeatCollectionFiles(DateTimeModel):
    beat = models.ForeignKey(
        Beats,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_collection_files",
    )
    audio_file = models.ForeignKey(
        BeatAudioFiles,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_collection_files",
    )
    collection = models.ForeignKey(
        BeatCollections,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="beat_collection_files",
    )
