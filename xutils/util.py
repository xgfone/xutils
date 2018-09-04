# -*- coding: utf-8 -*-
import sys
import json
import os.path

from subprocess import STDOUT, CalledProcessError, check_output as _check_output
from xutils import major, minor, to_unicode, is_string


def json_loads(s, **kwargs):
    """Fix the type of s on Python 3.0 ~ 3.5 to be compatible with Python 2.7
    or Python 3.6+."""

    if major == 3 and minor < 6 and isinstance(s, (bytes, bytearray)):
        s = s.decode(kwargs.get("encoding", "utf-8"))
    return json.loads(s, **kwargs)


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


def subprocess_exception_to_str(exc, encoding=None):
    if isinstance(exc, CalledProcessError):
        if hasattr(exc, "stderr") and exc.stderr:
            return to_unicode(exc.stderr, encoding) if encoding else exc.stderr
        if exc.output:
            return to_unicode(exc.output, encoding) if encoding else exc.output
    return str(exc)


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


def load_py_file(filename):
    if not os.path.exists(filename):
        raise RuntimeError("'%r' doest't exist" % filename)

    cfg = {'__builtins__': __builtins__, '__file__': filename}
    execpyfile(filename, cfg, cfg)
    return cfg


###############################################################################
# For the follow codes, copy from gunicorn/_compat.py
#

def _check_if_pyc(fname):
    """Return True if the extension is .pyc, False if .py
    and None if otherwise"""
    from imp import find_module
    from os.path import realpath, dirname, basename, splitext

    # Normalize the file-path for the find_module()
    filepath = realpath(fname)
    dirpath = dirname(filepath)
    module_name = splitext(basename(filepath))[0]

    # Validate and fetch
    try:
        fileobj, fullpath, (_, _, pytype) = find_module(module_name, [dirpath])
    except ImportError:
        raise IOError("Cannot find config file. "
                      "Path maybe incorrect! : {0}".format(filepath))
    return pytype, fileobj, fullpath


def _get_codeobj(pyfile):
    """ Returns the code object, given a python file """
    from imp import PY_COMPILED, PY_SOURCE

    result, fileobj, fullpath = _check_if_pyc(pyfile)

    # WARNING:
    # fp.read() can blowup if the module is extremely large file.
    # Lookout for overflow errors.
    try:
        data = fileobj.read()
    finally:
        fileobj.close()

    # This is a .pyc file. Treat accordingly.
    if result is PY_COMPILED:
        # .pyc format is as follows:
        # 0 - 4 bytes: Magic number, which changes with each create of .pyc file.
        #              First 2 bytes change with each marshal of .pyc file. Last 2 bytes is "\r\n".
        # 4 - 8 bytes: Datetime value, when the .py was last changed.
        # 8 - EOF: Marshalled code object data.
        # So to get code object, just read the 8th byte onwards till EOF, and
        # UN-marshal it.
        import marshal
        code_obj = marshal.loads(data[8:])

    elif result is PY_SOURCE:
        # This is a .py file.
        code_obj = compile(data, fullpath, 'exec')

    else:
        # Unsupported extension
        raise Exception("Input file is unknown format: {0}".format(fullpath))

    # Return code object
    return code_obj


if major >= 3:
    def execpyfile(fname, *args):
        if fname.endswith(".pyc"):
            code = _get_codeobj(fname)
        else:
            code = compile(open(fname, 'rb').read(), fname, 'exec')
        return __builtins__['exec'](code, *args)
else:
    def _exec(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    def execpyfile(fname, *args):
        """ Overriding PY2 execfile() implementation to support .pyc files """
        if fname.endswith(".pyc"):
            return _exec(_get_codeobj(fname), *args)
        return execfile(fname, *args)
