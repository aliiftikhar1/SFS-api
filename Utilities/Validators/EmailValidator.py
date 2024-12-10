import re


class EmailValidator:
    def __init__(self, email=None):
        self.email = email

    def is_valid(self, email=""):
        if self.email:
            return re.match(r"[^@]+@[^@]+\.[^@]+", self.email)
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)
