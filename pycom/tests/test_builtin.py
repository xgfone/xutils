# encoding: utf-8
import unittest
from pycom import builtin


class BuiltinTests(unittest.TestCase):
    def setUp(self):
        # builtin.set_builtins([("_", lambda v: v)])
        builtin.set_builtins({"_": lambda v: v})

    def tearDown(self):
        if hasattr(builtin.builtins, "_"):
            builtin.remove_builtins("_")

    def test_set_builtin(self):
        self.assertEqual(_("test"), "test")

    def test_set_builtin_force_false(self):
        with self.assertRaises(AttributeError):
            builtin.set_builtin("_", lambda v: v)

    def test_set_builtin_force_true(self):
        self.assertIsNone(builtin.set_builtin("_", lambda v: v, True))

    def test_remove_builtins(self):
        self.assertIsNone(builtin.remove_builtins("_"))

    def test_remove_builtins_raise(self):
        with self.assertRaises(AttributeError):
            builtin.remove_builtins("attr")
