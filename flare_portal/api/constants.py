from typing import List, TypedDict

from flare_portal.experiments.constants import ModuleConfigType

ExperimentType = TypedDict("ExperimentType", {"id": int, "name": str})

ConfigType = TypedDict(
    "ConfigType", {"experiment": ExperimentType, "modules": List[ModuleConfigType]},
)
