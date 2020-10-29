from django import forms

from . import constants
from .models import User


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    roles = forms.MultipleChoiceField(choices=constants.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean(self) -> dict:
        cleaned_data = super().clean()

        if cleaned_data.get("password") != cleaned_data.get("password2"):
            raise forms.ValidationError({None: "The passwords do not match."})

        return cleaned_data

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit)
        user.set_password(self.cleaned_data["password"])

        for role in self.cleaned_data["roles"]:
            user.grant_role(role)

        if commit:
            user.save()

        return user
