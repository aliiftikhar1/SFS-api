from Utilities.Enums.BaseEnum import BaseEnum


class Boolean(BaseEnum):
    TRUE = True
    FALSE = False
    SMALL_TRUE = "true"
    SMALL_FALSE = "false"

    @staticmethod
    def get_bool(value: bool):
        if value in [Boolean.TRUE, Boolean.SMALL_TRUE]:
            return True
        elif value in [Boolean.FALSE, Boolean.SMALL_FALSE]:
            return False
