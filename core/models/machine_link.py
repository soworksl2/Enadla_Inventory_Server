from datetime import datetime
from dataclasses import dataclass

from core.helpers import model_helper

@dataclass
class MachineLink:
    machine_id: str = None
    email_linked: str = None
    link_creation_date: datetime = None

    @classmethod
    def from_dict(cls, **kwargs):
        return model_helper.create_obj(cls, **kwargs)
