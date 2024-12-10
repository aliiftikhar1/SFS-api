from Utilities.Enums.BaseEnum import BaseEnum


class RequestMethods(BaseEnum):
    GET = "Get"
    POST = "Post"
    PUT = "Put"
    PATCH = "Patch"
    DELETE = "Delete"

    @staticmethod
    def get_validate_methods():
        return [
            RequestMethods.POST.value,
            RequestMethods.PUT.value,
            RequestMethods.PATCH.value,
        ]

    @staticmethod
    def get_do_not_validate_methods():
        return [RequestMethods.GET.value, RequestMethods.DELETE.value]
