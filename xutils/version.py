# -*- coding: utf-8 -*-

try:
    from pbr.version import VersionInfo
except ImportError:
    VersionInfo = None

import logging
LOG = logging.getLogger(__name__)


def get_app_version(name, default='Unknown'):
    '''Return the version of the application by its name.'''
    if VersionInfo:
        try:
            return VersionInfo(name).version_string()
        except Exception:
            pass
    else:
        LOG.warning("please install the package 'pbr' first to get the version")
    return default
