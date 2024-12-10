from django.db import models

from User_Management.models import DateTimeModel, SoftDelete, User


class Chat(DateTimeModel, SoftDelete):
    title = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver"
    )
    description = models.CharField(max_length=1000, default="", blank=True)


class Messages(DateTimeModel, SoftDelete):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    message = models.CharField(max_length=2000)
