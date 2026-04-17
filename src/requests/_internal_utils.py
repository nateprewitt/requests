"""
requests._internal_utils
~~~~~~~~~~~~~~

Provides utility functions that are consumed internally by Requests
which depend on extremely few external helpers (such as compat)
"""

import importlib
import re
import warnings

# -------------------
# Character Detection
# -------------------


def _resolve_char_detection():
    """Find supported character detection libraries."""
    _chardet = None
    for lib in ("chardet", "charset_normalizer"):
        if _chardet is None:
            try:
                _chardet = importlib.import_module(lib)
            except ImportError:
                pass
    return _chardet


chardet = _resolve_char_detection()


class DefaultCharDetector:
    """Wraps the auto-resolved detection library and emits a FutureWarning.

    This is used as the default char_detector during the deprecation period
    to notify users that character detection will become optional.
    """

    def detect(self, data):
        warnings.warn(
            "Automatic character detection is being used but will be removed "
            "as a default in a future release of Requests. To continue using "
            "character detection, install a supported library and configure "
            "it with requests.set_char_detector(). To suppress this warning "
            "and fall back to UTF-8, call requests.set_char_detector(None).",
            FutureWarning,
            stacklevel=2,
        )
        return chardet.detect(data)


char_detector = DefaultCharDetector() if chardet is not None else None

_VALID_HEADER_NAME_RE_BYTE = re.compile(rb"^[^:\s][^:\r\n]*\Z")
_VALID_HEADER_NAME_RE_STR = re.compile(r"^[^:\s][^:\r\n]*\Z")
_VALID_HEADER_VALUE_RE_BYTE = re.compile(rb"^\S[^\r\n]*\Z|^\Z")
_VALID_HEADER_VALUE_RE_STR = re.compile(r"^\S[^\r\n]*\Z|^\Z")

_HEADER_VALIDATORS_STR = (_VALID_HEADER_NAME_RE_STR, _VALID_HEADER_VALUE_RE_STR)
_HEADER_VALIDATORS_BYTE = (_VALID_HEADER_NAME_RE_BYTE, _VALID_HEADER_VALUE_RE_BYTE)
HEADER_VALIDATORS = {
    bytes: _HEADER_VALIDATORS_BYTE,
    str: _HEADER_VALIDATORS_STR,
}


def to_native_string(string, encoding="ascii"):
    """Given a string object, regardless of type, returns a representation of
    that string in the native string type, encoding and decoding where
    necessary. This assumes ASCII unless told otherwise.
    """
    if isinstance(string, str):
        out = string
    else:
        out = string.decode(encoding)

    return out


def unicode_is_ascii(u_string):
    """Determine if unicode string only contains ASCII characters.

    :param str u_string: unicode string to check. Must be unicode
        and not Python 2 `str`.
    :rtype: bool
    """
    assert isinstance(u_string, str)
    try:
        u_string.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False
