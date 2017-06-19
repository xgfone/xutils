# encoding: utf-8
import sys

# On Python(>=2.7), sys.version_info[0] <==> sys.version_info.major
if sys.version_info[0] == 2:
    PY2, PY3 = True, False
    byte_type, text_type, string_type = str, unicode, basestring
else:
    PY2, PY3 = False, True
    byte_type, text_type, string_type = bytes, str, str

Bytes, Unicode, String = byte_type, text_type, string_type
to_bytes = lambda v, e="utf-8": v.encode(e) if isinstance(v, Unicode) else v
to_unicode = lambda v, e="utf-8": v.decode(e) if isinstance(v, Bytes) else v
to_str = to_unicode if PY3 else to_bytes
