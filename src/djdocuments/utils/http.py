import unicodedata
import warnings

from django.utils import six
from django.utils.encoding import force_text
from django.utils.six.moves.urllib.parse import urlparse


class RemovedInDjango21Warning(PendingDeprecationWarning):
    pass


def is_safe_url(url, host=None, allowed_hosts=None, require_https=False):
    """
    Return ``True`` if the url is a safe redirection (i.e. it doesn't point to
    a different host and uses a safe scheme).
    Always returns ``False`` on an empty url.
    If ``require_https`` is ``True``, only 'https' will be considered a valid
    scheme, as opposed to 'http' and 'https' with the default, ``False``.
    """
    if url is not None:
        url = url.strip()
    if not url:
        return False
    if six.PY2:
        try:
            url = force_text(url)
        except UnicodeDecodeError:
            return False
    if allowed_hosts is None:
        allowed_hosts = set()
    if host:
        warnings.warn(
            "The host argument is deprecated, use allowed_hosts instead.",
            RemovedInDjango21Warning,
            stacklevel=2,
        )
        # Avoid mutating the passed in allowed_hosts.
        allowed_hosts = allowed_hosts | {host}
    # Chrome treats \ completely as / in paths but it could be part of some
    # basic auth credentials so we need to check both URLs.
    return (_is_safe_url(url, allowed_hosts, require_https=require_https) and
            _is_safe_url(url.replace('\\', '/'), allowed_hosts, require_https=require_https))


def _is_safe_url(url, allowed_hosts, require_https=False):
    # Chrome considers any URL with more than two slashes to be absolute, but
    # urlparse is not so flexible. Treat any url with three slashes as unsafe.
    if url.startswith('///'):
        return False
    url_info = urlparse(url)
    # Forbid URLs like http:///example.com - with a scheme, but without a hostname.
    # In that URL, example.com is not the hostname but, a path component. However,
    # Chrome will still consider example.com to be the hostname, so we must not
    # allow this syntax.
    if not url_info.netloc and url_info.scheme:
        return False
    # Forbid URLs that start with control characters. Some browsers (like
    # Chrome) ignore quite a few control characters at the start of a
    # URL and might consider the URL as scheme relative.
    if unicodedata.category(url[0])[0] == 'C':
        return False
    scheme = url_info.scheme
    # Consider URLs without a scheme (e.g. //example.com/p) to be http.
    if not url_info.scheme and url_info.netloc:
        scheme = 'http'
    valid_schemes = ['https'] if require_https else ['http', 'https']
    return ((not url_info.netloc or url_info.netloc in allowed_hosts) and
            (not scheme or scheme in valid_schemes))
