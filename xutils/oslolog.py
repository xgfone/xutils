# coding: utf-8
"""
Use the library 'oslo.log' to configure the logging.

Applications should use oslo.log’s configuration functions to register
logging-related configuration options and configure the root and other default
loggers.

(1) Call register_options() before parsing command line options.
(2) Call set_defaults() before configuring logging.
(3) Call setup() to configure logging for the application.

## Example

import sys
from oslo_log.log import register_options, set_defaults, setup


def set_log(conf, project, args=None, version="unknown", default_log_levels=None):
    # Register the command line and configuration options used by oslo.log.
    register_options(conf)

    # Set default values for the configuration options used by oslo.log.
    set_defaults(default_log_levels=default_log_levels)

    # Parse the command line options.
    args = args if args else sys.argv[1:]
    conf(args, project=project, version=version)

    # Setup logging for the current application.
    setup(conf, project, version)

"""
