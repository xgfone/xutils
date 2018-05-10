# -*- coding: utf-8 -*-

import sys

major, minor, micro = sys.version_info[:3]
if major < 3:
    PY3, Unicode, Bytes = False, unicode, str
else:
    PY3, Unicode, Bytes = True, str, bytes


def to_bytes(v, encoding="utf-8", errors="strict"):
    if isinstance(v, Bytes):
        return v
    elif isinstance(v, Unicode):
        return v.encode(encoding, errors)
    return to_bytes(str(v), encoding=encoding, errors=errors)


def to_unicode(v, encoding="utf-8", errors="strict"):
    if isinstance(v, Bytes):
        return v.decode(encoding, errors)
    elif isinstance(v, Unicode):
        return v
    return to_unicode(str(v), encoding=encoding, errors=errors)


to_str = to_unicode if PY3 else to_bytes
is_bytes = lambda s: isinstance(s, Bytes)
is_unicode = lambda s: isinstance(s, Unicode)
is_string = lambda s: isinstance(s, (Bytes, Unicode))


class Object(object):
    def __repr__(self):
        ss = ("%s=%s" % (k, v) for k, v in vars(self).items() if not k.startswith("_"))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(ss))
