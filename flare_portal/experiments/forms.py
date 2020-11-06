from django import forms

from .models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ["name", "description", "code", "owner", "project"]
        widgets = {"project": forms.HiddenInput()}
