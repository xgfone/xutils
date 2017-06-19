# encoding: utf8
import re
import sys
import random
import netaddr
import logging
import netifaces

if sys.version_info[0] == 2:
    PY3 = False
    text_type = unicode
else:
    PY3 = True
    text_type = str

LOG = logging.getLogger(__name__)
_ = (lambda v: v)

LOCALHOST4 = "127.0.0.1"
LOCALHOST6 = "[::1]"


def get_ip(if_or_ip=None, default=None, ipv6=False):
    """Get the IP information.

    If the argument is the valid IPv4 or IPv6, return it directly. Or, it is
    considered as the interface's name, then return its IP. If fails, return
    the local ip that is in the same network as the gateway, or "127.0.0.1"
    or "[:]".

    When the argument is the interface's name, if `ipv6` is True, return IPv6,
    or return IPv4.
    """
    try:
        ok = netaddr.valid_ipv4(if_or_ip) or netaddr.valid_ipv6(if_or_ip)
        if ok:
            return if_or_ip
    except Exception:
        pass

    if ipv6:
        af_inet = netifaces.AF_INET6
        default = default or LOCALHOST6
    else:
        af_inet = netifaces.AF_INET
        default = default or LOCALHOST4

    if not if_or_ip:
        gtw = netifaces.gateways()
        try:
            if_or_ip = gtw['default'][af_inet][1]
        except Exception:
            return default

    try:
        return netifaces.ifaddresses(if_or_ip)[af_inet][0]['addr']
    except Exception:
        return default


def parse_server_string(server_str):
    """Parses the given server_string and returns a tuple of host and port.
    If it's not a combination of host part and port, the port element
    is an empty string. If the input is invalid expression, return a tuple of
    two empty strings.
    """
    try:
        # First of all, exclude pure IPv6 address (w/o port).
        if netaddr.valid_ipv6(server_str):
            return (server_str, '')

        # Next, check if this is IPv6 address with a port number combination.
        if server_str.find("]:") != -1:
            (address, port) = server_str.replace('[', '', 1).split(']:')
            return (address, port)

        # Third, check if this is a combination of an address and a port
        if server_str.find(':') == -1:
            return (server_str, '')

        # This must be a combination of an address and a port
        (address, port) = server_str.split(':')
        return (address, port)
    except (ValueError, netaddr.AddrFormatError):
        LOG.error(_('Invalid server_string: %s'), server_str)
        return ('', '')


def is_valid_ipv6_cidr(address):
    try:
        netaddr.IPNetwork(address, version=6).cidr
        return True
    except (TypeError, netaddr.AddrFormatError):
        return False


def get_shortened_ipv6(address):
    addr = netaddr.IPAddress(address, version=6)
    return str(addr.ipv6())


def get_shortened_ipv6_cidr(address):
    net = netaddr.IPNetwork(address, version=6)
    return str(net.cidr)


def is_valid_cidr(address):
    """Check if address is valid

    The provided address can be a IPv6 or a IPv4
    CIDR address.
    """
    try:
        # Validate the correct CIDR Address
        netaddr.IPNetwork(address)
    except netaddr.AddrFormatError:
        return False

    # Prior validation partially verify /xx part
    # Verify it here
    ip_segment = address.split('/')

    if (len(ip_segment) <= 1 or
            ip_segment[1] == ''):
        return False

    return True


def get_ip_version(network):
    """Returns the IP version of a network (IPv4 or IPv6).

    Raises AddrFormatError if invalid network.
    """
    if netaddr.IPNetwork(network).version == 6:
        return "IPv6"
    elif netaddr.IPNetwork(network).version == 4:
        return "IPv4"


def safe_ip_format(ip):
    """Transform ip string to "safe" format.

    Will return ipv4 addresses unchanged, but will nest ipv6 addresses
    inside square brackets.
    """
    try:
        if netaddr.IPAddress(ip).version == 6:
            return '[%s]' % ip
    except (TypeError, netaddr.AddrFormatError):  # hostname
        pass
    # it's IPv4 or hostname
    return ip


def sanitize_hostname(hostname):
    """Return a hostname which conforms to RFC-952 and RFC-1123 specs."""
    if isinstance(hostname, text_type):
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
