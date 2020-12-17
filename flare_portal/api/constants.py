from typing import List, TypedDict

from flare_portal.experiments.constants import ModuleConfigType

ExperimentType = TypedDict(
    "ExperimentType",
    {
        "id": int,
        "name": str,
        "description": str,
        "trial_length": float,
        "rating_delay": float,
        "iti_min_delay": int,
        "iti_max_delay": int,
        "rating_scale_anchor_label_left": str,
        "rating_scale_anchor_label_center": str,
        "rating_scale_anchor_label_right": str,
    },
)

ConfigType = TypedDict(
    "ConfigType",
    {"experiment": ExperimentType, "modules": List[ModuleConfigType]},
)
