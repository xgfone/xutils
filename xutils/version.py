# coding: utf-8

# Define the minimum and maximum version of the API across all of the
# REST API. The format of the version is:
# X.Y.Z where:
#
# - X will only be changed if a significant backwards incompatible API
# change is made which affects the API as whole. That is, something
# that is only very very rarely incremented.
#
# - Y when you make any change to the API. Note that this includes
# semantic changes which may not affect the input or output formats or
# even originate in the API code layer. We are not distinguishing
# between backwards compatible and backwards incompatible changes in
# the versioning system. It must be made clear in the documentation as
# to what is a backwards compatible change and what is a backwards
# incompatible one.
#
# - Z is only used to fix a bug and it's OPTIONAL.
from __future__ import absolute_import, print_function

import re

_ = (lambda v: v)


def get_program_version(program_name):
    import pbr
    return pbr.version.VersionInfo(program_name).version_string()


class Version(object):
    """This class represents an API Version Request with convenience
    methods for manipulation and comparison of version
    numbers that we need to do to implement microversions.
    """

    def __init__(self, version_string=None):
        """Create an API version request object.

        :param version_string: String representation of Version.
            Correct format is 'X.Y', where 'X' and 'Y' are int values.
            None value should be used to create Null Version,
            which is equal to 0.0
        """
        self.major = 0
        self.minor = 0

        if version_string is not None:
            match = re.match(r"^([1-9]\d*)\.([1-9]\d*|0)(\.([1-9]\d*|0)){0,1}$",
                             version_string)
            if match:
                self.major = int(match.group(1))
                self.minor = int(match.group(2))
                self.micro = int(match.group(4)) if match.group(4) else 0
            else:
                msg = "Version <{0}> is not supported".format(version_string)
                raise ValueError(msg)

    def __str__(self):
        """Debug/Logging representation of object."""
        return "Version<major={0}, minor={1}, micro={2}>".format(self.major,
                                                                 self.minor,
                                                                 self.micro)

    def is_null(self):
        return self.major == 0 and self.minor == 0 and self.micro == 0

    def _format_type_error(self, other):
        return TypeError(_("'%(other)s' should be an instance of '%(cls)s'") %
                         {"other": other, "cls": self.__class__})

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise self._format_type_error(other)

        return ((self.major, self.minor, self.micro) <
                (other.major, other.minor, other.micro))

    def __eq__(self, other):
        if not isinstance(other, Version):
            raise self._format_type_error(other)

        return ((self.major, self.minor, self.micro) ==
                (other.major, other.minor, other.micro))

    def __gt__(self, other):
        if not isinstance(other, Version):
            raise self._format_type_error(other)

        return ((self.major, self.minor, self.micro) >
                (other.major, other.minor, other.micro))

    def __le__(self, other):
        return self < other or self == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __ge__(self, other):
        return self > other or self == other

    def match(self, min_version, max_version):
        """Returns whether the version object represents a version
        greater than or equal to the minimum version and less than
        or equal to the maximum version.

        @param min_version: Minimum acceptable version.
        @param max_version: Maximum acceptable version.
        @returns: boolean

        If min_version is null then there is no minimum limit.
        If max_version is null then there is no maximum limit.
        If self is null then raise ValueError.
        """

        if self.is_null():
            raise ValueError
        if max_version.is_null() and min_version.is_null():
            return True
        elif max_version.is_null():
            return min_version <= self
        elif min_version.is_null():
            return self <= max_version
        else:
            return min_version <= self <= max_version

    def get_string(self):
        """Converts object to string representation which if used to create
        an Version object results in the same version request.
        """
        if self.is_null():
            raise ValueError
        return "{0}.{1}.{2}".format(self.major, self.minor, self.micro)


class VersionedMethod(object):

    def __init__(self, name, start_version, end_version, func):
        """Versioning information for a single method
        @name: Name of the method
        @start_version: Minimum acceptable version
        @end_version: Maximum acceptable_version
        @func: Method to call
        Minimum and maximums are inclusive
        """
        self.name = name
        self.start_version = start_version
        self.end_version = end_version
        self.func = func

    def __str__(self):
        return ("Version Method {0}: min: {1}, max: {2}".format(self.name,
                self.start_version, self.end_version))


if __name__ == '__main__':
    v = Version("1.2")
    v1 = Version("1.1")
    v2 = Version("1.2.1")
    print(v)
    print(v.get_string())
    print(v.match(v1, v2))
