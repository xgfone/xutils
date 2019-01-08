# -*- coding: utf-8 -*-

import os
import sys
import os.path

from argparse import ArgumentParser
from xutils import PY3, is_string


def find_config_file(name, dir=None, extra_dirs=("/opt", "/etc"), ext=".conf",
                     env=False):
    """Find the config file path.

    If name has no ext, it will be appended with the argument ext.
    If dir is empty, it will be the current directory by default.
    If env is True, it will find the configuration file firstly
    from the environ variable, name, which will be converted to the upper.

    The lookup order is as follow,
    /{dir}/{name}/{name}.conf
    /opt/{name}/{name}.conf
    /etc/{name}/{name}.conf
    /{dir}/{name}.conf
    /opt/{name}.conf
    /etc/{name}.conf
    """

    name, fext = os.path.splitext(name)
    if env:
        filename = os.environ.get(name.upper(), None)
        if filename and os.path.exists(filename):
            return filename

    filename = name + ext if not fext or fext == "." else name
    path = os.path.abspath(os.path.expanduser(dir if dir else "."))

    dirs = list(extra_dirs) if extra_dirs else []
    if path not in dirs:
        dirs = [path] + dirs
    dirs = [os.path.join(d, name) for d in dirs] + dirs

    for d in dirs:
        filepath = os.path.join(d, filename)
        if os.path.exists(filepath):
            return filepath

    raise RuntimeError("Not found '%s'" % filename)


class Option(object):
    def __init__(self, name, short=None, default=None, help=None, cli=None):
        self.name = name
        self.short = short
        self.default = default
        self.help = help
        self.cli = cli
        self._group = None

    def __call__(self, value):
        return self.parse(value)

    def parse(self, value):
        return value

    def validate(self, value):
        return value


class String(Option):
    def __init__(self, name, short=None, default=None, help=None, cli=None,
                 encoding='utf-8', empty=True, min_len=None, max_len=None):
        super(String, self).__init__(name, short=short, default=default,
                                     help=help, cli=cli)
        self._encoding = encoding
        self._empty = empty
        self._min_len = min_len
        self._max_len = max_len

    def parse(self, value):
        if PY3:
            if not isinstance(value, str):
                value = value.decode(self._encoding)
        else:
            if isinstance(value, str):
                value = value.decode(self._encoding)

        return self.validate(value)

    def validate(self, value):
        if self._empty is not None and not self._empty and not value:
            raise ValueError("'%s' in group '%s' is empty" % (self.name, self._group))

        if self._min_len is not None and len(value) < self._min_len:
            raise ValueError("the length of '%s' in group '%s' is less than '%d'" %
                             (self.name, self._group, self._min_len))

        if self._max_len is not None and len(value) > self._max_len:
            raise ValueError("the length of '%s' in group '%s' is greater than '%d'" %
                             (self.name, self._group, self._max_len))

        return value


class Bool(Option):
    TRUE = ["t", "1", "on", "true"]
    FALSE = ["f", "0", "off", "false"]

    def parse(self, value):
        if isinstance(value, bool):
            return value
        elif not is_string(value):
            return bool(value)

        value = value.lower()
        if value in Bool.TRUE:
            return True
        elif value in Bool.FALSE:
            return False
        raise ValueError("invalid bool value '{0}'".format(value))


class Number(Option):
    def __init__(self, name, short=None, default=None, help=None, cli=None,
                 min=None, max=None):
        super(Number, self).__init__(name, short=short, default=default,
                                     help=help, cli=cli)
        self._min = min
        self._max = max

    def validate(self, value):
        if self._min is not None and value < self._min:
            raise ValueError("the length of '%s' in group '%s' is less than '%d'" %
                             (self.name, self._group, self._min))

        if self._max is not None and value > self._max:
            raise ValueError("the length of '%s' in group '%s' is greater than '%d'" %
                             (self.name, self._group, self._max))

        return value


class Int(Number):
    def __init__(self, name, short=None, default=None, help=None, cli=None,
                 base=10, min=None, max=None):
        super(Int, self).__init__(name, short=short, default=default, help=help,
                                  cli=cli, min=min, max=max)
        self._base = base

    def parse(self, value):
        return self.validate(value if isinstance(value, int) else int(value, self._base))


class Float(Number):
    def __init__(self, name, short=None, default=None, help=None, cli=None,
                 min=None, max=None):
        super(Float, self).__init__(name, short=short, default=default,
                                    help=help, cli=cli, min=min, max=max)

    def parse(self, value):
        return self.validate(float(value))


class List(Option):
    def __init__(self, parser, name, short=None, default=None, help=None,
                 cli=None):
        super(List, self).__init__(name, short=short, default=default,
                                   help=help, cli=cli)
        self._parser = parser

    def parse(self, value):
        if isinstance(value, (list, tuple)):
            vs = value
        else:
            vs = (v.strip() for v in value.split(",") if v.strip())
        return tuple((self._parser(v) for v in vs))


class IntList(List):
    def __init__(self, name, short=None, default=None, help=None, cli=None,
                 base=10):
        super(IntList, self).__init__(Int("", base=base).parse, name,
                                      short=short, default=default, help=help,
                                      cli=cli)


class FloatList(List):
    def __init__(self, name, short=None, default=None, help=None, cli=None):
        super(FloatList, self).__init__(Float("", cli=cli).parse, name,
                                        short=short, default=default,
                                        help=help, cli=cli)


class StringList(List):
    def __init__(self, name, short=None, default=None, help=None, cli=None,
                 encoding='utf-8'):
        super(StringList, self).__init__(String("", encoding=encoding).parse,
                                         name, short=short, default=default,
                                         help=help, cli=cli)


class Group(object):
    def __init__(self, group_name):
        self.__name = group_name

    def __repr__(self):
        attrs = ("{0}={1}".format(k, v) for k, v in vars(self).items())
        return "{0}({1})".format(self.__class__.__name__, ", ".join(attrs))

    def __contains__(self, name):
        return hasattr(self, name)

    def __getattr__(self, name):
        e = "The group '{0}' has no the option '{1}'"
        raise AttributeError(e.format(self.__name, name))

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def __getitem__(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            e = "The group '{0}' has no the option '{1}'"
            raise KeyError(e.format(self.__name, name))

    def items(self):
        return vars(self).items()


class Configuration(object):
    __slots__ = ["_default_group_name", "_default_group", "_allow_empty",
                 "_parsed", "_caches", "_opts", "_description", "_version",
                 "_encoding", "_parse_string"]

    def __init__(self, description=None, allow_empty=False, encoding="utf-8",
                 default_group="DEFAULT", version=None):
        """A simple configuration file parser based on the format INI.

        When an configuration option does not exist, for getting one default
        value, not raising an exception, please use the method of get(), or the
        builtin function of getattr().
        """

        self._parsed = False
        self._description = description
        self._default_group_name = default_group
        self._default_group = Group(self._default_group_name)
        self._allow_empty = allow_empty
        self._version = version if version else "Unknown"
        self._encoding = encoding
        self._parse_string = String("", encoding=encoding).parse

        self._caches = {self._default_group_name: self._default_group}
        self._opts = {}

    def __getattr__(self, name):
        if not self._parsed:
            raise Exception("Not parsed")

        try:
            return self._caches[name]
        except KeyError:
            pass

        msg = "'{0}' object has no attribute '{1}'"
        raise AttributeError(msg.format(self.__class__.__name__, name))

    def __getitem__(self, name):
        if not self._parsed:
            raise Exception("Not parsed")

        _name = self._uniformize(name)
        try:
            return self._caches[_name]
        except KeyError:
            pass

        msg = "'{0}' has no key '{1}'"
        raise KeyError(msg.format(self.__class__.__name__, name))

    def __repr__(self):
        attrs = ("{0}={1}".format(k, v) for k, v in self._caches.items())
        return "{0}({1})".format(self.__class__.__name__, ", ".join(attrs))

    def _set_group_opt(self, group_name, opt_name, opt_value, force=False):
        opt_value = self._opts[group_name][opt_name].validate(opt_value)
        gname = group_name if group_name else self._default_group_name
        group = self._caches[gname]
        if hasattr(group, opt_name) and not force:
            e = "The group '{0}' has had the option of '{1}'"
            raise ValueError(e.format(gname, opt_name))
        setattr(self._caches[gname], opt_name, opt_value)

    def _uniformize(self, name):
        return name.replace("-", "_")

    def _unniformize(self, name):
        return name.replace("_", "-")

    def parsed(self):
        """Return True if it has been parsed, or False."""
        return self._parsed

    def parse_files(self, filenames=""):
        """Parse the INI configuration files.

        The argument is either a string standing for the path of the
        configuration file, or a list of them.
        """
        if self._parsed:
            raise Exception("Have been parsed")
        self._parsed = True

        if filenames:
            if not isinstance(filenames, (list, tuple)):
                filenames = self._parse_string(filenames).strip(", ").split(",")

            for filename in filenames:
                self._parse_file(filename)

        self._check_and_fix()

    def _check_and_fix(self):
        for gname, opts in self._opts.items():
            group = self._caches[gname]
            for name, opt in opts.items():
                if name in group:
                    continue
                elif opt.default is not None or isinstance(opt, Bool):
                    self._set_group_opt(gname, name, opt.default)
                    continue

                if not self._allow_empty:
                    msg = "The option '{0}' in the group '{1}' has no value."
                    raise ValueError(msg.format(name, gname))

        # Set the options in the default group into self.
        group = self._caches.pop(self._default_group_name)
        for key, value in group.items():
            if key in self._caches:
                msg = "'{0}' had has the value '{1}'"
                raise ValueError(msg.format(self.__class__.__name__, key))
            self._caches[key] = value

    def _parse_file(self, filename):
        filename = str(filename)
        with open(filename) as f:
            lines = f.readlines()

        gname = self._default_group_name
        index, max_index = 0, len(lines)
        while index < max_index:
            line = self._parse_string(lines[index]).strip()
            index += 1

            # Comment
            if not line or line[0] in ("#", "=", ";"):
                continue

            # Group Section
            if line[0] == "[":
                if line[-1] != "]":
                    m = ("the format of the group is wrong, "
                         "which must start with [ and end with ]")
                    raise ValueError(m)
                _gname = line[1:-1]
                if not _gname:
                    raise ValueError("the group name is empty")
                if _gname not in self._caches:
                    continue
                gname = _gname
                continue

            # Group Option Values
            items = line.split("=", 1)
            if len(items) != 2:
                raise ValueError("the format is wrong, must contain '=': " + line)

            name, value = self._uniformize(items[0].strip()), items[1].strip()

            # Handle the continuation line
            if value[-1:] == "\\":
                values = [value.rstrip("\\").strip()]
                while index < max_index:
                    value = lines[index].strip()
                    values.append(value.rstrip("\\").strip())
                    index += 1
                    if value[-1:] != "\\":
                        break
                value = "\n".join(values)

            opt = self._opts[gname].get(name, None)
            if opt:
                self._set_group_opt(gname, name, opt(value))

    def register_opt(self, opt, group=None, cli=None):
        if not isinstance(opt, Option):
            raise ValueError("the option must be the subclass of Option")

        if self._parsed:
            raise Exception("Have been parsed")

        name = self._uniformize(opt.name)
        group = self._uniformize(group or self._default_group_name)
        self._opts.setdefault(group, {})

        if name in self._opts[group]:
            raise KeyError("The option {0} has been regisetered".format(name))

        opt._group = group
        if isinstance(cli, bool):
            opt.cli = cli
        self._opts[group][name] = opt
        self._caches[group] = Group(group)

    def register_opts(self, opts, group=None, cli=None):
        for opt in opts:
            self.register_opt(opt, group=group, cli=cli)

    def register_bool(self, name, short=None, default=None, group=None,
                      help=None, cli=True):
        """Register the bool option.

        The value of this option will be parsed to the type of bool.
        """
        opt = Bool(name, short=short, default=default, help=help, cli=cli)
        self.register_opt(opt, group=group)

    def register_int(self, name, short=None, default=None, group=None,
                     help=None, cli=True, base=10):
        """Register the int option.

        The value of this option will be parsed to the type of int.
        """
        opt = Int(name, short=short, default=default, help=help, cli=cli,
                  base=base)
        self.register_opt(opt, group=group)

    def register_float(self, name, short=None, default=None, group=None,
                       help=None, cli=True):
        """Register the float option.

        The value of this option will be parsed to the type of float.
        """
        opt = Float(name, short=short, default=default, help=help, cli=cli)
        self.register_opt(opt, group=group)

    def register_str(self, name, short=None, default=None, group=None,
                     help=None, cli=True, encoding='utf-8'):
        """Register the str option.

        The value of this option will be parsed to the type of str.
        """
        opt = String(name, short=short, default=default, help=help, cli=cli,
                     encoding=encoding)
        self.register_opt(opt, group=group)

    def register_int_list(self, name, short=None, default=None, group=None,
                          help=None, cli=True, base=10):
        """Register the int list option.

        The value of this option will be parsed to the type of int list.
        """
        opt = IntList(name, short=short, default=default, help=help, cli=cli,
                      base=base)
        self.register_opt(opt, group=group)

    def register_str_list(self, name, short=None, default=None, group=None,
                          help=None, cli=True, encoding='utf-8'):
        """Register the string list option.

        The value of this option will be parsed to the type of string list.
        """
        opt = StringList(name, short=short, default=default, help=help,
                         cli=cli, encoding=encoding)
        self.register_opt(opt, group=group)

    def register_float_list(self, name, short=None, default=None, group=None,
                            help=None, cli=True):
        """Register the float list option.

        The value of this option will be parsed to the type of float list.
        """
        opt = FloatList(name, short=short, default=default, help=help, cli=cli)
        self.register_opt(opt, group=group)

    ###########################################################################
    # Parse CLI
    def parse(self, *args, **kwargs):
        return self.parse_cli(*args, **kwargs)

    def parse_cli(self, args=None, config_file_name="config-file"):
        """Parse the cli options."""
        if self._parsed:
            raise Exception("Have been parsed")
        self._parsed = True

        if args is None:
            args = sys.argv[1:]
        if not args:
            self._check_and_fix()
            return None

        gopts, args = self._parser_cli(args, description=self._description,
                                       config_file_name=config_file_name)
        if getattr(args, "version", False):
            print(self._version)
            sys.exit(0)

        if config_file_name:
            config_file = getattr(args, self._uniformize(config_file_name), "")
            for filename in config_file.split(","):
                filename = filename.strip()
                if filename:
                    self._parse_file(filename)

        for cli_opt, (gname, name) in gopts.items():
            opt = self._opts[gname][name]
            value = getattr(args, cli_opt, None)
            if value:
                value = opt.parse(value)
                if isinstance(opt, Bool):
                    if opt.default is None:
                        if value:
                            self._set_group_opt(gname, name, value, force=True)
                    elif value != opt.default:
                        self._set_group_opt(gname, name, value, force=True)
                elif value != opt.default:
                    self._set_group_opt(gname, name, value, force=True)

        self._check_and_fix()
        return args

    def _parser_cli(self, args, description=None, config_file_name=None):
        cli = ArgumentParser(description=description)
        if config_file_name:
            cli.add_argument("--" + config_file_name, default="",
                             help="The config file path.")
        cli.add_argument("--version", action="store_true",
                         help="Print the version and exit.")

        group_opts = {}
        for gname, opts in self._opts.items():
            if gname == self._default_group_name:
                group = cli
            else:
                group = cli.add_argument_group(gname)

            for name, opt in opts.items():
                if not opt.cli:
                    continue

                action = None
                default = opt.default
                if isinstance(opt, Bool):
                    action = "store_false" if default else "store_true"
                    default = False if default is None else default

                if gname == self._default_group_name:
                    opt_name = self._unniformize(name)
                    opt_key = self._uniformize(name)
                else:
                    opt_name = self._unniformize("{0}-{1}".format(gname, name))
                    opt_key = self._uniformize(opt_name)
                group_opts[opt_key] = (gname, name)
                short = opt.short
                short = "-" + short if short and short[0] != "-" else short
                names = [short, "--" + opt_name] if short else ["--" + opt_name]
                group.add_argument(*names, action=action, default=default,
                                   help=opt.help)

        return group_opts, cli.parse_args(args=args)
