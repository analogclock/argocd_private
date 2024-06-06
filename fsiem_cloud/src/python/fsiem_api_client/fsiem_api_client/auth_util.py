import hashlib
from json import loads
from fsiem_api_client.http_call import HttpCall

path_salt = '/phoenix/rest/h5/sec/loginInfo'


def get_salt(http: HttpCall, super_url: str, user='admin') -> str:
    """Gets the salt from the super with which to add to the password"""
    url = f'{super_url}{path_salt}'
    json = {'organization': 'super', 'userName': user}
    # Note: This request must not have cookies, otherwise server will
    # respond with HTTP 403
    r = http.post(url, json=json, use_cookies=False, verbose=False)
    if r.text == '"Invalid username or password."':
        raise ValueError('License may not have been inserted')
    salt_dict = loads(r.text)
    salt = salt_dict['salt']
    return salt


def salt_new_password(password: str, salt: str) -> str:
    """Hashes the password and retrieved salt with sha1 - specific format
    for the new password when setting storage

    Parameters
    ----------
    password : str
        The new password
    salt : str
        The salt retrieved from the API

    Returns
    -------
    str
        The hashed and salted password
    """
    salted = salt + password
    hash = hashlib.sha1(salted.encode('utf-8')).hexdigest().upper()
    return f'{salt}|{hash}'
