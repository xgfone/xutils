# encoding: utf-8
import unittest
from xutils.objects import AttrWrapper


class ObjectsTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ObjectsTests, self).__init__(*args, **kwargs)

    def test_attr_wrapper_yes(self):
        class TestAttrWrapper(AttrWrapper):
            attrs = ["attr"]
        obj = TestAttrWrapper()
        obj.attr = "attr"
        self.assertEquals(obj.attr, "attr")

    def test_attr_wrapper_no(self):
        class TestAttrWrapper(AttrWrapper):
            attrs = []
        obj = TestAttrWrapper()
        with self.assertRaises(AttributeError):
            obj.attr = "attr"
