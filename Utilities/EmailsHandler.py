import json
import os
import smtplib
from random import randint

from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, BadHeaderError
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from Soul_Family_Sounds.settings import BASE_DIR
from User_Management.models import User


class EmailsHandler:
    def __init__(self, to_user: User = None):
        self.token = self.subject = self.body = self.user_email = None
        self.email_user = os.environ.get("EMAIL_USER")
        self.email_PASSWORD = os.environ.get("EMAIL_PASSWORD")

        if to_user:
            self.user = to_user
            self.user_email = self.user.email
            self.uid = urlsafe_base64_encode(force_bytes(to_user.pk))
            self.token = default_token_generator.make_token(self.user)

    @staticmethod
    def __read_template(template_path: str):
        with open(
                os.path.join(BASE_DIR, f"templates/emails/{template_path}"), "r"
        ) as file:
            html_content = file.read()
        return html_content

    @staticmethod
    def __replace_otp_in_html(content: str, otp: str):
        for index, new_value in enumerate(otp):
            placeholder = f"{{otp_{index}}}"
            content = content.replace(placeholder, new_value)
        return content

    @staticmethod
    def __replace_interview_date_in_html(content: str, date):
        formatted_date = date.strftime("%d")

        formatted_day = f"{formatted_date}{'th' if 11 <= int(formatted_date) <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(int(formatted_date) % 10, 'th')}"

        formatted_month = date.strftime("%B")

        placeholder = "{{date}}"
        date = f"{formatted_day} {formatted_month}"

        content = content.replace(placeholder, date)
        return content

    def set_confirmation_email(self, otp: str, email: str, user_details: str):
        """This function sets subject and body of confirmation of email"""
        self.user_email = email
        string = f"{otp}+{user_details}+{otp[::-1]}"
        self.token = urlsafe_base64_encode(force_bytes(string))

        self.subject = "Verify Your Email - Soul Sounds Family"
        content = self.__read_template("verify-email-template.html")
        self.body = self.__replace_otp_in_html(content, otp)

        return self

    def set_welcome_email(self):
        self.subject = "Welcome - Soul Sounds Family"
        self.body = self.__read_template("welcome-template.html")
        return self

    def set_request_accepted_supplier_email(self, interview_date):
        self.subject = "Congratulations - Soul Sounds Family"
        content = self.__read_template("supplier-request-accepted-template.html")
        self.body = self.__replace_interview_date_in_html(content, interview_date)
        return self

    def set_supplier_request__email(self):
        self.subject = "Supplier Request - Soul Sounds Family"
        self.body = self.__read_template("supplier-request-template.html")
        return self

    def set_confirmed_email(self):
        """This function sets subject and body of email is confirmed."""

        self.subject = "Email Verified - Soul Sounds Family"
        self.body = f"Your Email Verified Successfully!"

        return self

    def set_new_supplier_email(self, password):
        """This function sets subject and body for new supplier."""

        self.subject = "Account Credentials- Soul Sounds Family"
        self.body = (
            f'Your account has been created as "Supplier" on Soul Family Sounds.\n'
            f"Login using Credentials:\n"
            f"- Email: {self.user_email}\n"
            f"- Password: {password}"
        )

        return self

    def set_update_email(self, update, email=None):
        """This function sets subject and body of update email"""
        self.user_email = email
        self.subject = f"{update} Changed - Soul Sounds Family"
        self.body = (
            f"Your {update.lower()} is changed.\nIf you have not changed, reach us at: "
            f"https://www.soulfamilysounds.com/support/"
        )

        return self

    def set_verify_otp_email(self, otp: str):
        """This function sets token, subject and body of verify otp email"""
        string = f"{otp}+{self.user.email}+{otp[::-1]}+{self.token}"

        self.token = urlsafe_base64_encode(force_bytes(string))
        self.subject = "Reset Password Email - Soul Sounds Family"
        content = self.__read_template(f"reset-password-template-{randint(0, 1)}.html")
        self.body = self.__replace_otp_in_html(content, otp)

        return self

    def set_account_deletion_otp_email(self, otp: str):
        """This function sets token, subject and body of verify otp email"""
        string = f"{otp}+{self.user.email}+{otp[::-1]}+{self.token}"

        self.token = urlsafe_base64_encode(force_bytes(string))
        self.subject = "Account Deletion Email - Soul Sounds Family"
        content = self.__read_template(f"account-delete-template.html")
        self.body = self.__replace_otp_in_html(content, otp)

        return self

    @staticmethod
    def split_token(token: str):
        """This function splits the token on '+'"""
        string = smart_str(urlsafe_base64_decode(token))
        return string.split("+")

    @staticmethod
    def validate_verify_otp_email(otp: str, token: str, user=None):
        """This functions validates the verify otp email"""
        try:
            l_otp, email, r_otp, token = EmailsHandler.split_token(token)

            if not user:
                user = User.objects.filter(
                    email=email, is_active=True, is_deleted=False
                ).first()

            check_token = default_token_generator.check_token(user, token)
            check_otp = otp == l_otp == r_otp[::-1]

            if not user or not check_token:
                return "token"
            elif not check_otp:
                return "otp"
            return "valid"
        except (TypeError, ValueError, OverflowError):
            return "unknown"

    @staticmethod
    def validate_confirmation_email(otp: str, token: str):
        """This functions validates the verification email"""
        try:
            l_otp, user_details, r_otp = EmailsHandler.split_token(token)
            check_otp = otp == l_otp == r_otp[::-1]

            if not check_otp:
                return "otp"
            return json.loads(user_details)

        except (TypeError, ValueError, OverflowError):
            return "unknown"

    def send(self):
        """This functions sends the email"""
        try:
            email = EmailMessage(
                from_email=self.email_user,
                to=[self.user_email],
                subject=self.subject,
                body=self.body,
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
        except (
                smtplib.SMTPException
                or BadHeaderError
                or smtplib.SMTPAuthenticationError
                or ValidationError
        ) as error:
            raise Exception(f"{error}an error occurred while sending the email!")
