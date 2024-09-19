from enum import Enum


class Category(Enum):
    PATIENT = "Patient"
    ENCOUNTER = "Encounter"
    PATIENT_ADDRESS = "PatientAddress"
    PATIENT_PHONE = "PatientPhone"

    @property
    def value_str(self):
        return self.value
