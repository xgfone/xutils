# -*- coding: utf-8 -*-

from subprocess import STDOUT, CalledProcessError, check_output as _check_output
from xutils import major, minor, to_unicode, is_string


def check_output(cmd, timeout=None, encoding=None, stderr=None, **kwargs):
    """Wrap subprocess.check_output() with ``timeout``, ``encoding`` and ``stderr``.

    If ``stderr`` is True, it will capture the standard error in the result.
    If ``stderr`` is None or False, it will ignore the standard error.

    (NOTE): It will wrap the CalledProcessError exception, then reraise it
    by RuntimeError.
    """

    if major >= 3 and minor >= 3:
        kwargs["timeout"] = timeout

    if stderr is True:
        stderr = STDOUT
    elif stderr is False:
        stderr = None

    try:
        out = _check_output(cmd, stderr=stderr, **kwargs)
    except CalledProcessError as err:
        raise RuntimeError(err.output or str(err))
    return to_unicode(out, encoding) if encoding else out


def which(command, reraise=False, encoding="utf-8", which="/usr/bin/which"):
    """Find and return the absolute path list of ``command`` used by ``which``.

    If not found, raise a ``RuntimeError`` exception if ``reraise`` is ``True``,
    or return an empty list.
    """

    if not is_string(command):
        raise ValueError("the first argument 'command' must be string")

    try:
        out = check_output([which, command], timeout=3, encoding=encoding,
                           stderr=True)
        return [line for line in out.split("\n") if line]
    except CalledProcessError as err:
        if reraise:
            raise RuntimeError(err.output or str(err))
        return []
