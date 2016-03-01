# encoding: utf-8
from __future__ import print_function
import sys
import subprocess

# On Python(>=2.7), sys.version_info[0] <==> sys.version_info.major
if sys.version_info[0] == 2:
    PY3 = False
else:
    PY3 = True


def _map2(func, *iterable):
    """This function is equal to the built-in function, map, in Python2.
    But it returns a iterator, not a list.

    If one iterable is shorter than another it is assumed to be extended with
    None items. And if function is None, the identity function is assumed.
    """
    def inner():
        args = []
        num = 0
        for iter in iterable:
            data = next(iter, None)
            if data is None:
                num += 1
            args.append(data)
        return num, args

    iterable = [iter(it) for it in iterable]
    total = len(iterable)
    func = func if func else id
    while True:
        num, args = inner()
        if num == total:
            raise StopIteration
        else:
            yield func(args)


def _map3(func, *iterable):
    """This function is equal to the built-in function, map, in Python3.

    If one iterable is longer than another it will be truncated.
    If function is None, the identity function is assumed.
    """
    iterable = [iter(it) for it in iterable]
    func = func if func else id
    while True:
        result = []
        for it in iterable:
            result.append(next(it))
        yield func(result)

if PY3:
    map2 = _map2
    map3 = map
else:
    # map2 = map
    map2 = _map2
    map3 = _map3


if getattr(subprocess, "check_output", None):
    check_output = subprocess.check_output
else:
    def check_output(*popenargs, **kwargs):
        r"""Run command with arguments and return its output as a byte string.

        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.

        The arguments are the same as for the Popen constructor.  Example:

        >>> check_output(["ls", "-l", "/dev/null"])
        'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

        The stdout argument is not allowed as it is used internally.
        To capture standard error in the result, use stderr=STDOUT.

        >>> check_output(["/bin/sh", "-c",
        ...               "ls -l non_existent_file ; exit 0"],
        ...              stderr=STDOUT)
        'ls: non_existent_file: No such file or directory\n'
        """
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd, output=output)
        return output

    subprocess.check_output = check_output
