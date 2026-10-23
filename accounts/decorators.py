from functools import wraps

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.shortcuts import resolve_url


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(
                    request.get_full_path(),
                    resolve_url(settings.LOGIN_URL),
                )
            if request.user.role != role:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator
