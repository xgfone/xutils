# encoding: utf-8
import sys

# On Python(>=2.7), sys.version_info[0] <==> sys.version_info.major
if sys.version_info[0] == 2:
    PY3 = False
else:
    PY3 = True


try:
    from pycom.builtin import set_builtin
except ImportError:
    if PY3:
        import builtins
    else:
        import __builtin__ as builtins

    def set_builtin(name, value, force=False):
        try:
            getattr(builtins, name)
        except AttributeError:
            pass
        else:
            if not force:
                raise AttributeError("{0} has already existed".format(name))
        setattr(builtins, name, value)
finally:
    set_builtin("PY3", PY3)
