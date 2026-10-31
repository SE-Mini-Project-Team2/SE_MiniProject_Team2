from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import EmailAuthenticationForm, RegistrationForm


def home(request):
    return render(request, "home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your account was created. You can now log in.",
            )
            return redirect("accounts:login")
        messages.error(
            request,
            "Please correct the errors below to create your account.",
        )
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


class EmailLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        messages.success(self.request, "You have been logged in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Unable to log in. Check your email and password and try again.",
        )
        return super().form_invalid(form)


@login_required
@require_POST
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")
