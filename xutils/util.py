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


def which(command, which="/usr/bin/which"):
    """Find and return the first absolute path of command used by `which`.

    If not found, return "".
    """

    try:
        return check_output([which, command]).split("\n")[0]
    except Exception:
        return ""
