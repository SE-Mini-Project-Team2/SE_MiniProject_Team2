from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from .models import User, UserRole


class RegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=UserRole.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("name", "email", "role")

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        return email.lower()


class EmailAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(label="Email")

    def __init__(self, request=None, *args, **kwargs):
        data = kwargs.get("data")
        if data is not None and "email" not in data and "username" in data:
            data = data.copy()
            data["email"] = data["username"]
            kwargs["data"] = data

        super().__init__(request, *args, **kwargs)
        self.fields.pop("username")

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email.strip().lower(),
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return cleaned_data
