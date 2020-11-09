from typing import TypedDict

ModuleConfigType = TypedDict(
    "ModuleConfigType", {"id": int, "type": str, "config": dict}
)
