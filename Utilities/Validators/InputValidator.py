class InputValidator:
    def __init__(self, field_value: str or list):
        if isinstance(field_value, list):
            self.field_value = field_value
        else:
            self.field_value = str(field_value)

    def is_valid(self):
        return (not (self.field_value.strip() is None)) and (
                self.field_value.strip() != ""
        )

    def is_(self, value):
        return self.field_value == str(value)

    def has_valid_length(self, min_length=0, max_length=-1):
        length = len(self.field_value)

        if not min_length or min_length < 0:
            min_length = 0

        if not max_length or max_length < 0:
            max_length = len(self.field_value)

        return min_length <= length <= max_length

    def is_valid_option(self, options):
        return self.field_value in options
