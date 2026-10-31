"""SEC-CTRL-16: temporary lockout after repeated failed logins.

Failures are counted per (email, client IP) pair in Django's cache. After
LOGIN_FAILURE_LIMIT consecutive failures the pair is locked for
LOGIN_LOCKOUT_SECONDS, even if the correct password is then supplied. A
successful login clears the counter.

Keying on email *and* IP means an attacker on another machine cannot lock a
real user out of their own account, while a single source still cannot keep
guessing passwords. Unknown emails are counted the same way as real ones, so
the lockout itself never reveals whether an account exists (SEC-CTRL-03).

Only REMOTE_ADDR is used for the IP. X-Forwarded-For is client-controlled and
would let an attacker reset their own counter by changing the header.
"""

import hashlib

from django.conf import settings
from django.core.cache import cache


DEFAULT_FAILURE_LIMIT = 5
DEFAULT_LOCKOUT_SECONDS = 15 * 60


def failure_limit():
    return getattr(settings, "LOGIN_FAILURE_LIMIT", DEFAULT_FAILURE_LIMIT)


def lockout_seconds():
    return getattr(settings, "LOGIN_LOCKOUT_SECONDS", DEFAULT_LOCKOUT_SECONDS)


def client_ip(request):
    if request is None:
        return ""
    return request.META.get("REMOTE_ADDR", "")


def _cache_key(email, ip):
    # Hash so raw email addresses never appear in cache keys.
    digest = hashlib.sha256(f"{email}|{ip}".encode("utf-8")).hexdigest()
    return f"login-failures:{digest}"


def is_locked_out(email, ip):
    return cache.get(_cache_key(email, ip), 0) >= failure_limit()


def record_failure(email, ip):
    """Count one failed attempt and return the new total."""
    key = _cache_key(email, ip)
    timeout = lockout_seconds()

    if cache.add(key, 1, timeout):
        count = 1
    else:
        try:
            count = cache.incr(key)
        except ValueError:
            # The entry expired between add() and incr().
            cache.set(key, 1, timeout)
            count = 1

    if count >= failure_limit():
        # Start the full lockout window from the attempt that triggered it.
        cache.touch(key, timeout)

    return count


def reset_failures(email, ip):
    cache.delete(_cache_key(email, ip))
