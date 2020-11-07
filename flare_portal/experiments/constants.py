from typing import Literal, TypedDict

ModuleType = Literal["FEAR_CONDITIONING"]

ModuleConfigType = TypedDict(
    "ModuleConfigType", {"id": int, "type": ModuleType, "config": dict}
)
