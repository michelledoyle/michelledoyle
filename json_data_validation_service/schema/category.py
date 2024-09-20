from enum import Enum


class Category(Enum):
    INFO = "Info"
    ADDRESS = "Address"
    IDENTIFICATION = "Identification"
    PHONE = "Phone"
    EMAIL = "Email"

    @property
    def value_str(self):
        return self.value
