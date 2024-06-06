from ipaddress import ip_address, IPv4Address, IPv6Address
from socket import gethostbyname_ex
from typing import Tuple


def check_if_ip(addresses: list) -> Tuple[list, list]:
    """Divide input worker addresses into dns record and ipv4 addresses. Will
    drop any ipv6 addresses as they are currently unsupported by fsiem

    Parameters
    ----------
    addresses : list
        List of worker addresses

    Returns
    -------
    Tuple[list, list]
        A list of worker ipv4 addresses
        A list of worker dns records
    """
    ipv4s = []
    dns = []
    for address in addresses:
        if check_if_ipv4(address):
            ipv4s.append(address)
        elif check_if_ipv6(address):
            print(f'Dropped worker ipv6 address `{address}`.'
                  ' We can only support ipv4')
        else:
            print(f'Assume `{address}` is DNS, it is not detected as an IP')
            dns.append(address)
    return ipv4s, dns


def resolve_dns_to_ipv4(hostnames: list) -> list:
    """Attempt to resolve a list of worker dns addresses to ipv4 addresses.
    Will drop any resolved ipv6 addresses as they are currently unsupported by
    fsiem

    Parameters
    ----------
    hostnames : list
        List of worker dns addresses

    Returns
    -------
    list
        A list of worker ipv4 addresses
    """
    ipv4s = []
    for hostname in hostnames:
        try:
            ip_list = gethostbyname_ex(hostname)[2]
        except Exception as e:
            print(f'Unable to resolve hostname, skipping: `{hostname}`')
            print(e)
            continue
        for ip in ip_list:
            if check_if_ipv4(ip):
                ipv4s.append(ip)
            elif check_if_ipv6(ip):
                print(f'Dropped resolved ipv6 address `{hostname}`.'
                      ' We can only support ipv4')
    return ipv4s


def check_if_ipv4(address: str) -> bool:
    """Check if a string is an ipv4 address

    Parameters
    ----------
    address : str
        The string to be checked

    Returns
    -------
    bool
        True if the string is an ipv4 address, False if not
    """
    try:
        if isinstance(ip_address(address), IPv4Address):
            return True
    except ValueError:
        return False


def check_if_ipv6(address: str) -> bool:
    """Check if a string is an ipv6 address

    Parameters
    ----------
    address : str
        The string to be checked

    Returns
    -------
    bool
        True if the string is an ipv6 address, False if not

    Raises
    ------
    Exception
        Unexpected error when checking the string
    """
    try:
        if isinstance(ip_address(address), IPv6Address):
            return True
    except ValueError:
        return False


def strip_https(url: str) -> str:
    """Stripped http or https from URL

    Parameters
    ----------
    url : str
        The url to amend

    Returns
    -------
    str
        The amended url
    """
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    return url
