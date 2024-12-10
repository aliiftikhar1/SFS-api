from django.db.models import TextChoices


class BaseEnum(TextChoices):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
