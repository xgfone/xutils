# encoding: utf-8
import unittest
from xutils import osloi18n as i18n


class OsloI18nTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(OsloI18nTests, self).__init__(*args, **kwargs)
        self.str = "test"

    def test__(self):
        try:
            i18n._("")
        except Exception as err:
            self.assertTrue(ValueError == err.__class__)
        else:
            self.assertEquals(self.str, i18n._(self.str))

    def test_C(self):
        try:
            i18n._("")
        except Exception as err:
            self.assertTrue(ValueError == err.__class__)
        else:
            self.assertEquals("('context', '%s')" % self.str, i18n._C("context", self.str))

    def test_P(self):
        try:
            i18n._("")
        except Exception as err:
            self.assertTrue(ValueError == err.__class__)
        else:
            self.assertEquals("('test1', 'test2', 'test3')", i18n._P("test1", "test2", "test3"))

    def test_LI(self):
        try:
            i18n._("")
        except Exception as err:
            self.assertTrue(ValueError == err.__class__)
        else:
            self.assertEquals(self.str, i18n._LI(self.str))

    def test_LC(self):
        try:
            i18n._("")
        except Exception as err:
            self.assertTrue(ValueError == err.__class__)
        else:
            self.assertEquals(self.str, i18n._LC(self.str))

    def test_LE(self):
        try:
            i18n._("")
        except Exception as err:
            self.assertTrue(ValueError == err.__class__)
        else:
            self.assertEquals(self.str, i18n._LE(self.str))

    def test_LW(self):
        try:
            i18n._("")
        except Exception as err:
            self.assertTrue(ValueError == err.__class__)
        else:
            self.assertEquals(self.str, i18n._LW(self.str))
