# -*- coding: utf-8 -*-

from subprocess import check_output
from xutils import to_unicode, is_string


def which(command, reraise=False, encoding="utf-8", which="/usr/bin/which"):
    """Find and return the absolute path list of ``command`` used by ``which``.

    If not found, raise a ``RuntimeError`` exception if ``reraise`` is ``True``,
    or return an empty list.
    """

    if not is_string(command):
        raise ValueError("the first argument 'command' must be string")

    try:
        lines = to_unicode(check_output([which, command]), encoding).split("\n")
        cmds = [line for line in lines if line]
    except Exception:
        cmds = []

    if cmds or not reraise:
        return cmds
    raise RuntimeError("not found '%s'" % command)
