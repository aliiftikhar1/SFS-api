from django.db.models import Count, Q

from User_Management.models import User
from Utilities.Enums import UserType, SubmissionStatus


def find_approval_person():
    staff = User.objects.prefetch_related("packs_review").filter(usertype=UserType.STAFF.value)
    data = {}
    for user in staff:
        packs_count = user.packs_review.filter(
            status__in=[SubmissionStatus.UPLOADED.value, SubmissionStatus.PROCESS.value])
        data[user] = packs_count

    next_approval_person = staff.prefetch_related("packs_review").annotate(
        num_packs=Count('packs_review__pack',
                        filter=Q(packs_review__status=SubmissionStatus.UPLOADED.value))
    ).filter(num_packs__lt=1000).order_by('num_packs')

    if next_approval_person.exists():
        return next_approval_person.first()
    else:
        return None
