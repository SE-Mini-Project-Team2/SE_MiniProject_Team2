from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

from .security_log import email_reference, log_event


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request=None, **kwargs):
    # SEC-CTRL-18: the password in `credentials` is never read or logged.
    email = str(credentials.get("username") or credentials.get("email") or "")
    user = (
        get_user_model().objects.filter(email__iexact=email).only("pk").first()
        if email
        else None
    )
    log_event(
        "login_failed",
        request=request,
        user_id=user.pk if user else "unknown",
        email_ref=email_reference(email),
    )
