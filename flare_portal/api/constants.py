from typing import List, TypedDict

from flare_portal.experiments.constants import ModuleConfigType

ExperimentType = TypedDict(
    "ExperimentType",
    {
        "id": int,
        "name": str,
        "rating_delay": float,
        "rating_scale_anchor_label_left": str,
        "rating_scale_anchor_label_center": str,
        "rating_scale_anchor_label_right": str,
    },
)

ConfigType = TypedDict(
    "ConfigType", {"experiment": ExperimentType, "modules": List[ModuleConfigType]},
)
