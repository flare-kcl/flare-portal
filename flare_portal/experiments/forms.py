from django import forms

from .models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = [
            "name",
            "description",
            "code",
            "owner",
            "project",
            "trial_length",
            "rating_delay",
            "rating_scale_anchor_label_left",
            "rating_scale_anchor_label_center",
            "rating_scale_anchor_label_right",
        ]
        widgets = {"project": forms.HiddenInput()}
