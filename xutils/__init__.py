# -*- coding: utf-8 -*-

import sys
import logging

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
LOG = logging.getLogger("gunicorn.error" if "gunicorn" in sys.modules else None)


class Object(object):
    def __repr__(self):
        ss = ("%s=%s" % (k, v) for k, v in vars(self).items() if not k.startswith("_"))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(ss))


class AttributeProxy(Object):
    def __init__(self, obj):
        '''The argument may be a dict or object.'''
        self._is_dict = isinstance(obj, dict)
        self._obj = obj

    def __contains__(self, name):
        return name in self._obj if self._is_dict else hasattr(self._obj, name)

    def __getattr__(self, name):
        if self._is_dict:
            try:
                return self._obj[name]
            except KeyError:
                raise AttributeError("'%s' object has no attribute '%s'" %
                                     (self._obj.__class__.__name__, name))
        else:
            try:
                return getattr(self._obj, name)
            except AttributeError:
                raise AttributeError("'%s' object has no attribute '%s'" %
                                     (self._obj.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name == '_is_dict' or name == '_obj':
            object.__setattr__(self, name, value)
            return

        if self._is_dict:
            self._obj[name] = value
        else:
            setattr(self._obj, name, value)

    def __setitem__(self, name, value):
        if self._is_dict:
            self._obj[name] = value
        else:
            setattr(self._obj, name, value)

    def __getitem__(self, name):
        if self._is_dict:
            return self._obj[name]

        try:
            return getattr(self._obj, name)
        except AttributeError:
            raise KeyError(name)

    def items(self):
        if self._is_dict:
            return self._obj.items()
        return vars(self._obj).items()
