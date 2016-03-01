# encoding: utf-8
import unittest

from xutils import const


class ConstTests(unittest.TestCase):
    def test_const_set(self):
        const.ATTR1 = "attr"
        self.assertEqual("attr", const.ATTR1)

    def test_const_reset(self):
        const.ATTR2 = "attr"
        with self.assertRaises(const.ConstError):
            const.ATTR2 = "other"

    def test_const_case(self):
        with self.assertRaises(const.ConstCaseError):
            const.attr = "attr"
