# -*- coding: utf-8 -*-

from subprocess import check_output
from xutils import to_unicode


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
