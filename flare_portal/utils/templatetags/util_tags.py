import json
import os
import re
from typing import Any, Dict

from django import forms, template
from django.db.models.fields.files import FieldFile
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context: Dict[str, Any], path: str) -> str:
    if context.get("request") and re.search(path, context["request"].path):
        return "active"
    return ""


@register.simple_tag
def alpine_field_defaults(form: forms.Form) -> str:
    """Returns a JSON object of the fields of a form for use with Alpine.js"""
    # Add a default value for sortorder because that field is controlled
    # as a special case
    defaults = {"sortorder": 0}
    return mark_safe(
        json.dumps({**{field.name: None for field in form}, **defaults}).replace(
            '"', "'"
        )
    )


@register.simple_tag
def get_formset_form(formset: forms.BaseFormSet) -> forms.BaseForm:
    """Constructs a sample form from the formset"""
    return formset._construct_form(0, **formset.get_form_kwargs(0))  # type: ignore


@register.inclusion_tag("includes/form-group.html")
def alpine_field(field: forms.BoundField, index: str) -> dict:
    name = field.html_name.replace("-0-", f"-{index}-")
    field.field.widget.attrs["x-bind:name"] = f"`{name}`"
    field.field.widget.attrs["x-model"] = f"form.{field.name}"

    return {"field": field}


@register.filter
def filename(value: FieldFile) -> str:
    return os.path.basename(value.file.name)
