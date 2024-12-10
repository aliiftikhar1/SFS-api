from django.urls import path

from Product_Management.MainStream import GetPacksView, GetSamplesView, GetMIDIView, GetPresetView, ViewPackView, \
    CollectionsView, CollectionsAddView, CollectionsRemoveView, CollectionsDropDownView, DownloadsView, \
    ViewDownloadsView, ViewFileDownloadsView, ViewCollectionView, LikeView, UnlikeView, ViewLikesView
from Product_Management.Views import GenresView, SubGenresView, GenresDropdownView, InstrumentsView, \
    SubInstrumentsView, InstrumentsDropdownView, MoodsView, MoodsDropdownView, PackSubmissionsView, ViewPacksView, \
    PluginsDropdownView, SendRevisionPacksView, ResolveRevisionPacksView, ApproveRevisionPacksView, PluginsView, \
    RejectRevisionPacksView, SubmitForReviewView, ApprovePackView, RejectPackView, ViewSubmittedPacksView

urlpatterns = [
    # Main Stream

    # Discover Page
    path("explore/discover", GetPacksView.as_view()),

    # Products
    path("products/view-pack", ViewPackView.as_view()),
    path("products/samples", GetSamplesView.as_view()),
    path("products/midi", GetMIDIView.as_view()),
    path("products/preset", GetPresetView.as_view()),

    # My Library
    path("mylibrary/likes/view-likes", ViewLikesView.as_view()),
    path("mylibrary/likes/like", LikeView.as_view()),
    path("mylibrary/likes/unlike", UnlikeView.as_view()),

    # Downloads
    path("mylibrary/downloads/view", ViewDownloadsView.as_view()),
    path("mylibrary/downloads/view-pack", ViewFileDownloadsView.as_view()),
    path("mylibrary/downloads/download", DownloadsView.as_view()),

    # Collections
    path("mylibrary/collection", CollectionsView.as_view()),
    path("mylibrary/collection/view", ViewCollectionView.as_view()),
    path("mylibrary/collection/dropdown", CollectionsDropDownView.as_view()),
    path("mylibrary/collection/add-file", CollectionsAddView.as_view()),
    path("mylibrary/collection/remove-file", CollectionsRemoveView.as_view()),

    # Manage Categories APIs
    path("moods/", MoodsView.as_view()),
    path("plugins/", PluginsView.as_view()),

    # Manage Genre APIs
    path("genres/", GenresView.as_view()),
    path("sub-genres/", SubGenresView.as_view()),

    # Manage Instruments APIs
    path("instruments/", InstrumentsView.as_view()),
    path("sub-instruments/", SubInstrumentsView.as_view()),

    # Dropdowns
    path("drp/genres/", GenresDropdownView.as_view()),
    path("drp/plugins/", PluginsDropdownView.as_view()),
    path("drp/instruments/", InstrumentsDropdownView.as_view()),
    path("drp/moods/", MoodsDropdownView.as_view()),

    # Manage Submissions
    path("pack-submission/", PackSubmissionsView.as_view()),
    path("view-packs/", ViewPacksView.as_view()),
    path("revise-pack/", SendRevisionPacksView.as_view()),
    path("resolve-revision/", ResolveRevisionPacksView.as_view()),
    path("approve-file/", ApproveRevisionPacksView.as_view()),
    path("reject-file/", RejectRevisionPacksView.as_view()),
    path("submit-for-review/", SubmitForReviewView.as_view()),
    path("view-submitted-packs/", ViewSubmittedPacksView.as_view()),
    path("approve-pack/", ApprovePackView.as_view()),
    path("reject-pack/", RejectPackView.as_view()),
]
