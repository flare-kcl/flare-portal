from typing import List, Optional, TypedDict

from flare_portal.experiments.constants import ModuleConfigType

ExperimentType = TypedDict(
    "ExperimentType",
    {
        "id": int,
        "name": str,
        "description": str,
        "contact_email": Optional[str],
        "trial_length": float,
        "rating_delay": float,
        "iti_min_delay": int,
        "iti_max_delay": int,
        "minimum_volume": float,
        "rating_scale_anchor_label_left": str,
        "rating_scale_anchor_label_center": str,
        "rating_scale_anchor_label_right": str,
        "us": str,
        "us_file_volume": float,
        "csa": str,
        "csb": str,
        "context_a": Optional[str],
        "context_b": Optional[str],
        "context_c": Optional[str],
        "gsa": Optional[str],
        "gsb": Optional[str],
        "gsc": Optional[str],
        "gsd": Optional[str],
        "reimbursements": bool,
    },
)

SiteConfigurationType = TypedDict(
    "SiteConfigurationType",
    {
        "terms_and_conditions": str,
    },
)

ConfigType = TypedDict(
    "ConfigType",
    {
        "experiment": ExperimentType,
        "config": SiteConfigurationType,
        "modules": List[ModuleConfigType],
    },
)

SubmissionType = TypedDict(
    "SubmissionType",
    {
        "participant_started_at": str,
        "participant_finished_at": str,
    },
)
