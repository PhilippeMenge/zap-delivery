import enum
import json
from dataclasses import asdict, is_dataclass


class CustomJsonEncoder(json.JSONEncoder):
    """### A custom JSON encoder to handle dataclasses and enums"""

    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)

        if isinstance(obj, enum.Enum):
            return obj.value

        return super().default(obj)
