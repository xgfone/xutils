# encoding: utf8
import hashlib
import six

from oslo_utils import encodeutils


def get_hash_str(base_str):
    """Returns string that represents MD5 hash of base_str (in hex format).

    If base_str is a Unicode string, encode it to UTF-8.
    """
    if isinstance(base_str, six.text_type):
        base_str = base_str.encode('utf-8')
    return hashlib.md5(base_str).hexdigest()


def safe_truncate(value, length):
    """Safely truncates unicode strings such that their encoded length is
    no greater than the length provided.
    """
    b_value = encodeutils.safe_encode(value)[:length]

    # NOTE(chaochin) UTF-8 character byte size varies from 1 to 6. If
    # truncating a long byte string to 255, the last character may be
    # cut in the middle, so that UnicodeDecodeError will occur when
    # converting it back to unicode.
    decode_ok = False
    while not decode_ok:
        try:
            u_value = encodeutils.safe_decode(b_value)
            decode_ok = True
        except UnicodeDecodeError:
            b_value = b_value[:-1]
    return u_value
