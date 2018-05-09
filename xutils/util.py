# -*- coding: utf-8 -*-

from subprocess import check_output as _check_output
from xutils import PY3, to_unicode


if PY3:
    def check_output(cmd, timeout=None, encoding=None, **kwargs):
        return _check_output(cmd, timeout=timeout, encoding=encoding, **kwargs)
else:
    def check_output(cmd, timeout=None, encoding=None, **kwargs):
        out = _check_output(cmd, **kwargs)
        return to_unicode(out, encoding) if encoding else out


def which(command, default=None, encoding="utf-8", which="/usr/bin/which"):
    """Find and return the first absolute path of command used by `which`.

    If not found and default is not None, return default.
    Or reraise an exception.
    """

    try:
        return to_unicode(check_output([which, command]), encoding).split("\n")[0]
    except Exception:
        if default is not None:
            return default
        raise
