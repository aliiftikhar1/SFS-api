from django.urls import path

from Beats_Management.MainStream import GetBeatsView,  ViewBeatView, \
    CollectionsView, CollectionsAddView, CollectionsRemoveView, CollectionsDropDownView, DownloadsView, \
    ViewDownloadsView, ViewFileDownloadsView, ViewCollectionView, LikeView, UnlikeView, ViewLikesView, \
    GetAllBeatsView
    # GetSamplesView, GetMIDIView, GetPresetView
    
from Beats_Management.Views import BeatGenresView, BeatGenre,BeatSubGenresView, BeatGenresDropdownView, BeatInstrumentsView, \
    BeatSubInstrumentsView, BeatInstrumentsDropdownView, BeatMoodsView, BeatMoodsDropdownView, BeatsSubmissionsView, ViewBeatsView, \
    PluginsDropdownView, SendRevisionBeatsView, ResolveRevisionBeatsView, ApproveRevisionBeatsView, PluginsView, \
    RejectRevisionBeatsView, BeatSubmitForReviewView, ApproveBeatView, RejectBeatView, ViewSubmittedBeatsView

urlpatterns = [
    # Mainstream
    path("explore/discover", GetBeatsView.as_view()),

    # beats
    path("beats/view-beats", ViewBeatView.as_view()),
    path("beats/beats", GetAllBeatsView.as_view()),
    # path("beats/midi", GetMIDIView.as_view()),
    # path("beats/preset", GetPresetView.as_view()),

    # My Library
    path("mylibrary/likes/view-likes", ViewLikesView.as_view()),
    path("mylibrary/likes/like", LikeView.as_view()),
    path("mylibrary/likes/unlike", UnlikeView.as_view()),

    # Downloads
    path("mylibrary/downloads/view", ViewDownloadsView.as_view()),
    path("mylibrary/downloads/view-beat", ViewFileDownloadsView.as_view()),
    path("mylibrary/downloads/download", DownloadsView.as_view()),

    # Collections
    path("mylibrary/collection", CollectionsView.as_view()),
    path("mylibrary/collection/view", ViewCollectionView.as_view()),
    path("mylibrary/collection/dropdown", CollectionsDropDownView.as_view()),
    path("mylibrary/collection/add-file", CollectionsAddView.as_view()),
    path("mylibrary/collection/remove-file", CollectionsRemoveView.as_view()),

    # Manage Categories APIs
    path("moods/", BeatMoodsView.as_view()),
    path("plugins/", PluginsView.as_view()),

    # Manage Genre APIs
    path("genres/", BeatGenresView.as_view()),
    path("sub-genres/", BeatSubGenresView.as_view()),

    # Manage Instruments APIs
    path("instruments/", BeatInstrumentsView.as_view()),
    path("sub-instruments/", BeatSubInstrumentsView.as_view()),

    # Dropdowns
    path("drp/genres/", BeatGenresDropdownView.as_view()),
    path("drp/plugins/", PluginsDropdownView.as_view()),
    path("drp/instruments/", BeatInstrumentsDropdownView.as_view()),
    path("drp/moods/", BeatMoodsDropdownView.as_view()),

    # Manage Submissions
    path("beat-submission/", BeatsSubmissionsView.as_view()),
    path("view-beats/", ViewBeatsView.as_view()),
    path("revise-beat/", SendRevisionBeatsView.as_view()),
    path("resolve-revision/", ResolveRevisionBeatsView.as_view()),
    path("approve-file/", ApproveRevisionBeatsView.as_view()),
    path("reject-file/", RejectRevisionBeatsView.as_view()),
    path("submit-for-review/", BeatSubmitForReviewView.as_view()),
    path("view-submitted-beats/", ViewSubmittedBeatsView.as_view()),
    path("approve-beat/", ApproveBeatView.as_view()),
    path("reject-beat/", RejectBeatView.as_view()),
]
