from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from .models import User, UserRole
from .throttling import (
    client_ip,
    is_locked_out,
    record_failure,
    reset_failures,
)


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

    error_messages = {
        **AuthenticationForm.error_messages,
        # SEC-CTRL-16: shown for unknown and real emails alike, so it does
        # not reveal whether an account exists.
        "locked_out": (
            "Too many failed login attempts. Please try again later."
        ),
    }

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
            email = email.strip().lower()
            ip = client_ip(self.request)

            # SEC-CTRL-16: refuse before checking the password, so a locked
            # pair cannot keep testing guesses.
            if is_locked_out(email, ip):
                raise forms.ValidationError(
                    self.error_messages["locked_out"],
                    code="locked_out",
                )

            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
            if self.user_cache is None:
                record_failure(email, ip)
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
            reset_failures(email, ip)

        return cleaned_data
