# encoding: utf-8
import sys
import traceback


# On Python(>=2.7), sys.version_info[0] <==> sys.version_info.major
if sys.version_info[0] == 2:
    PY3 = False
else:
    PY3 = True

if PY3:
    import builtins
else:
    import __builtin__ as builtins

_CACHE_BUILTIN = {}


def set_builtin(name, value, force=False):
    if getattr(builtins, name) and not force:
        raise AttributeError("{0} has already existed".format(name))

    setattr(builtins, name, value)
    global _CACHE_BUILTIN
    _CACHE_BUILTIN[name] = value


def set_builtins(args, force=False):
    if args is None:
        return

    if isinstance(args, dict):
        args = args.items()

    for n, v in args:
        set_builtin(n, v, force)


def builtin_(f=lambda v: v, force=False):
    set_builtin("_", f, force)
    set_builtin("t", f, force)


def builtin_traceback(force=False):
    set_builtin("traceback", traceback.format_exc, force)


def builtin_all(others=None, force=False):
    builtin_(force=force)
    builtin_traceback(force=force)
    if others:
        set_builtins(others, force=force)


def remove_builtins(args):
    if args is None:
        return

    if not isinstance(args, (list, tuple)):
        args = [args]

    for arg in args:
        if arg not in _CACHE_BUILTIN:
            raise AttributeError("{0} doesn't exist".format(arg))
        delattr(builtins, arg)
        _CACHE_BUILTIN.pop(arg)
