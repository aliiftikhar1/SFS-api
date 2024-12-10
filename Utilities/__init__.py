import random
import string
from collections import defaultdict
from datetime import timezone, datetime

from rest_framework_simplejwt.tokens import RefreshToken


def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return f"{refresh.access_token}"


def extract_error_messages(error_messages: []):
    """Extract error messages of serializers"""
    error_msgs = []
    for errors in error_messages.values():
        for error in errors:
            error_msgs.append(error)
    return error_msgs


def generate_username(model, length=8):
    """This functon generates the random username of given length"""
    characters = string.ascii_letters + string.digits

    while True:
        # Generate a random username with the specified length
        username = "".join(random.choice(characters) for _ in range(length))

        # Check if the username already exists in the database
        if not model.objects.filter(username=username).exists():
            return username


def generate_otp(length=5):
    """This functon generates the random otp of given length"""
    numbers = string.digits
    otp = "".join(random.choice(numbers) for _ in range(length))
    return otp


def generate_humanize_time(created_at):
    if not created_at:
        return ""

    now = datetime.now(timezone.utc)
    diff = now - created_at

    if diff.days == 0:
        if diff.seconds < 60:
            return "just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds // 3600} hours ago"
    elif diff.days == 1:
        return "1 day ago"
    elif diff.days < 30:
        return f"{diff.days} days ago"
    elif diff.days < 365:
        return f"{diff.days // 30} months ago"
    else:
        return f"{diff.days // 365} years ago"


def group_by_attribute(data: list, attribute: str):
    grouped_data = defaultdict(list)
    for item in data:
        key = item.get(attribute)
        grouped_data[key].append(item)
    return grouped_data
