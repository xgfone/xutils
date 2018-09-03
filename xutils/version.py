# -*- coding: utf-8 -*-

try:
    from pbr.version import VersionInfo
except ImportError:
    VersionInfo = None


def get_app_version(name, default='Unknown'):
    '''Return the version of the application by its name.'''
    if VersionInfo:
        try:
            return VersionInfo(name).version_string()
        except Exception:
            pass
    return default
