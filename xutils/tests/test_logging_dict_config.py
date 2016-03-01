# encoding: utf-8

import unittest
from xutils.logging_dict_config import get_config


class LoggingTests(unittest.TestCase):

    def test_get_config_project(self):
        config = get_config("project")
        left = "/var/log/project/project.log"
        right = config["handlers"]["file"]["filename"]
        self.assertEqual(left, right)

    def test_get_config_config(self):
        conf = {
            "root": {
                "level": "INFO",
            }
        }
        config = get_config("project", config=conf)
        self.assertEqual("INFO", config["root"]["level"])
