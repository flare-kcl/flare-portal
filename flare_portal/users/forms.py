from typing import Any

from django import forms
from django.contrib.auth.password_validation import (
    password_validators_help_text_html,
    validate_password,
)
from django.utils.safestring import mark_safe

from . import constants
from .models import User


class HorizontalCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "widgets/horizontal_checkbox_select.html"
    option_template_name = "widgets/checkbox_option.html"


class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Leave blank if not changing.",
    )
    password2 = forms.CharField(
        label="Password confirmation",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Enter the same password as above, for verification.",
    )
    roles = forms.MultipleChoiceField(
        choices=constants.ROLE_CHOICES, widget=HorizontalCheckboxSelectMultiple
    )

    error_messages = {
        "duplicate_username": "A user with that username already exists.",
        "password_mismatch": "The two password fields didn't match.",
    }

    password_required = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if self.password_required:
            self.fields["password1"].help_text = mark_safe(
                password_validators_help_text_html()
            )
            self.fields["password1"].required = True
            self.fields["password2"].required = True

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password2 != password1:
            self.add_error(
                "password2",
                forms.ValidationError(
                    self.error_messages["password_mismatch"], code="password_mismatch",
                ),
            )

        return password2

    def validate_password(self) -> None:
        """
        Run the Django password validators against the new password. This must
        be called after the user instance in self.instance is populated with
        the new data from the form, as some validators rely on attributes on
        the user model.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 == password2:
            validate_password(password1, user=self.instance)

    def _post_clean(self) -> None:
        super()._post_clean()  # type: ignore

        try:
            self.validate_password()
        except forms.ValidationError as e:
            self.add_error("password2", e)

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)

        password = self.cleaned_data["password1"]
        if password:
            user.set_password(password)

        # Reset user roles and recreate them from the selected roles
        user.roles = []

        for role in self.cleaned_data["roles"]:
            user.grant_role(role)

        if commit:
            user.save()
            self.save_m2m()
        return user


class UserCreateForm(UserForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "job_title",
            "affiliation",
        ]


class UserUpdateForm(UserForm):
    password_required = False

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "job_title",
            "affiliation",
            "is_active",
            "password1",
            "password2",
            "roles",
        ]
