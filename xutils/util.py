# -*- coding: utf-8 -*-

from subprocess import check_output


def which(command, which="/usr/bin/which"):
    """Find and return the first absolute path of command used by `which`.

    If not found, return "".
    """

    try:
        return check_output([which, command]).split("\n")[0]
    except Exception:
        return ""
