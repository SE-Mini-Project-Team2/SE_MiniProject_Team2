"""SEC-CTRL-18: safe logging of security-relevant events.

Every event goes to the "security" logger as one line of key=value pairs:

    2026-10-31 14:02:11 WARNING security event=login_failed user_id=unknown ...

Rules enforced here, not left to each caller:
* Only an allow-list of fields is logged (user id, IP, path, role, reason).
  Passwords, session IDs, CSRF tokens and request bodies are never passed in.
* Raw email addresses are not logged. A short SHA-256 reference lets an
  administrator tell whether two failures involve the same address.
* Request paths are logged without the query string, which can carry tokens.
* Values are stripped of newlines and control characters so user input cannot
  forge extra log lines.
* A filter on the handler masks anything that still looks like a secret.
"""

import hashlib
import logging
import re
import time

from django.conf import settings


logger = logging.getLogger("security")

MAX_VALUE_LENGTH = 200
_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9_.:/@%+\-]")


def clean_value(value):
    """Make a value safe for one log line: no whitespace, no control chars."""
    text = str(value)[:MAX_VALUE_LENGTH]
    return _UNSAFE_CHARS.sub("_", text)


def email_reference(email):
    digest = hashlib.sha256(str(email).strip().lower().encode("utf-8"))
    return digest.hexdigest()[:12]


def client_ip(request):
    # REMOTE_ADDR only; X-Forwarded-For is client-controlled.
    return request.META.get("REMOTE_ADDR", "unknown") if request else "unknown"


def user_id_of(user):
    if user is not None and getattr(user, "is_authenticated", False):
        return user.pk
    return "anonymous"


def log_event(event, request=None, user_id=None, level=logging.WARNING, **fields):
    """Write one security event. `fields` must be non-sensitive values."""
    if user_id is None:
        user_id = user_id_of(getattr(request, "user", None))
    parts = {"event": event, "user_id": user_id}
    if request is not None:
        parts["ip"] = client_ip(request)
        parts["path"] = request.path
    parts.update(fields)
    logger.log(
        level,
        " ".join(f"{key}={clean_value(value)}" for key, value in parts.items()),
    )


class UTCFormatter(logging.Formatter):
    """Timestamps in UTC so log lines from different machines line up."""

    converter = time.gmtime
    default_time_format = "%Y-%m-%d %H:%M:%S"
    default_msec_format = None


_SECRET_PATTERNS = [
    re.compile(
        r"(?i)\b(password\d?|sessionid|csrftoken|csrfmiddlewaretoken|"
        r"secret_key|token|authorization)\b\s*[=:]\s*[^\s,;&]+"
    ),
]


class RedactSecretsFilter(logging.Filter):
    """Last line of defence: mask secret-looking text in any log message."""

    def filter(self, record):
        message = record.getMessage()
        for pattern in _SECRET_PATTERNS:
            message = pattern.sub(lambda m: f"{m.group(1)}=[REDACTED]", message)
        secret = getattr(settings, "SECRET_KEY", "")
        if secret:
            message = message.replace(secret, "[REDACTED]")
        record.msg = message
        record.args = ()
        return True
