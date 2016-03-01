# encoding: utf-8
import unittest
from xutils.url import URL


class BuiltinTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BuiltinTests, self).__init__(*args, **kwargs)

    def test_geturl(self):
        u = "https://www.example1.com/other/path/to/index.html?test1=test1&test2=test2#fragment"
        _url = "http://www.example.com/path/to/index.html"
        url = URL(_url)
        url.scheme = "https"
        url.netloc = "www.example1.com"
        url.path = "/other/path/to/index.html"
        url.query = "test1=test1&test2=test2"
        url.fragment = "fragment"
        self.assertEquals(url.geturl(), u)
