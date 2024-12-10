from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user
from rest_framework.exceptions import AuthenticationFailed


class CustomTokenValidationMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        user = self.validate_token(request)
        if user is None:
            user = get_user(request)
        request.user = user
        return self.get_response(request)

    def validate_token(self, request):
        auth_header = self.jwt_auth.get_header(request)
        if auth_header:
            try:
                raw_token = self.jwt_auth.get_raw_token(auth_header)
                validated_token = self.jwt_auth.get_validated_token(raw_token)
                user = self.jwt_auth.get_user(validated_token)

                if user.auth_token is None:
                    raise AuthenticationFailed()

                if all([user.is_active, (not user.is_deleted), user.auth_token == str(validated_token)]):
                    return user

            except AuthenticationFailed as e:
                raise Exception(str(e))
