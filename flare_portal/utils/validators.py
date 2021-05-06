from typing import List

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_ascending_order(values: List[float]) -> None:
    if not all(values[i] <= values[i + 1] for i in range(len(values) - 1)):
        raise ValidationError(_("Values must be in ascending order"))
