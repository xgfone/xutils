# -*- coding: utf-8 -*-

import re
import random

from socket import inet_aton, inet_ntoa
from struct import pack as struct_pack, unpack as struct_unpack
from xutils import PY3, is_unicode

_ALL_IP_MASK = 2 ** 32 - 1
_IP_MASK_CACHES = {}
for i in range(0, 33):
    _IP_MASK_CACHES[i] = (_ALL_IP_MASK >> i) ^ _ALL_IP_MASK


def normalize_ipv4_subnet(ip):
    ip, mask = ip.split("/")
    ip = struct_unpack("!I", inet_aton(ip))[0] & _IP_MASK_CACHES[int(mask)]
    return "{}/{}".format(inet_ntoa(struct_pack("!I", ip)), mask)


def sanitize_hostname(hostname):
    """Return a hostname which conforms to RFC-952 and RFC-1123 specs."""

    if is_unicode(hostname):
        # Remove characters outside the Unicode range U+0000-U+00FF
        hostname = hostname.encode('latin-1', 'ignore')
        if PY3:
            hostname = hostname.decode('latin-1')

    hostname = re.sub('[ _]', '-', hostname)
    hostname = re.sub(r'[^\w.-]+', '', hostname)
    hostname = hostname.lower()
    hostname = hostname.strip('.-')

    return hostname


def generate_mac_address():
    """Generate an Ethernet MAC address."""
    # NOTE(vish): We would prefer to use 0xfe here to ensure that linux
    #             bridge mac addresses don't change, but it appears to
    #             conflict with libvirt, so we use the next highest octet
    #             that has the unicast and locally administered bits set
    #             properly: 0xfa.
    #             Discussion: https://bugs.launchpad.net/nova/+bug/921838
    mac = [0xfa, 0x16, 0x3e,
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


class Mac(object):
    def __init__(self, mac, upper=False, unified=False):
        flag = "X" if upper else "x"
        width = "2" if unified else "1"
        formatter = "".join(("{0:0", width, flag, "}"))

        ms = []
        try:
            for i in mac.strip().lower().split(":"):
                ms.append(formatter.format(int(i, 16)))
        except ValueError:
            raise ValueError("The mac is invalid: {0}".format(mac))

        if len(ms) != 6:
            raise ValueError("The mac is invalid: {0}".format(mac))

        self.mac = ":".join(ms)

    def __eq__(self, other):
        if isinstance(other, Mac):
            return self.mac == other.mac
        elif isinstance(other, str):
            return self.mac == other
        else:
            return self.mac == str(other)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return self.mac
