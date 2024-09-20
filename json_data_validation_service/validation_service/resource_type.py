# resource_types.py
from enum import Enum

class ResourceType(Enum):
    INFO = "Info"
    ADDRESS = "Address"
    IDENTIFICATION = "Identification"
    EMAIL = "Email"
    PHONE = "Phone"
