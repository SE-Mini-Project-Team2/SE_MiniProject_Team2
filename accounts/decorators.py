from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render, resolve_url

from .security_log import log_event


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                log_event(
                    "access_denied",
                    request=request,
                    reason="unauthenticated",
                    required_role=role,
                )
                return redirect_to_login(
                    request.get_full_path(),
                    resolve_url(settings.LOGIN_URL),
                )
            if request.user.role != role:
                log_event(
                    "access_denied",
                    request=request,
                    reason="wrong_role",
                    required_role=role,
                    actual_role=request.user.role,
                )
                messages.error(
                    request,
                    "You do not have permission to access this page.",
                )
                return render(
                    request,
                    "accounts/forbidden.html",
                    status=403,
                )
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator
