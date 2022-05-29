import tkinter
import typing
import os

import requests


SESSION = requests.Session()
FIELDS_NAMES = (
    'Name', 'Registration',
    'Followers', 'Tweets'
)


if not os.path.isdir('data'):
    os.mkdir('data')


def check_internet() -> bool:
    """
        Сhecks internet connections.
    """

    try:
        SESSION.get('https://twitter.com', timeout=3)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        return False
    else:
        return True


def file_parser(path: str, is_proxy: bool = False) -> list:
    """
        Parse file.
    """

    if not path:
        return []

    with open(path, 'r', encoding='utf-8') as file:
        raw_data = file.readlines()

    if not is_proxy:
        data = [row.replace(' ', '').rsplit()[0].split(':', 1) for row in raw_data]
    else:
        data = [row.replace(' ', '').rsplit()[0] for row in raw_data]

    return data


def check_proxy(proxies: typing.Iterable[str]) -> str:
    """
        checks the proxy server for operability.
    """

    for proxy in proxies:
        try:
            SESSION.get('https://twitter.com', proxies={'http': proxy, 'https': proxy}, timeout=3)
            return proxy
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError):
            pass

    return ''


def write_account(status: str, user: str, password: str) -> None:
    """
        Create a file if it doesn't exist and append "Username: Password" to it.
    """

    with open(f'data/{status}.txt', 'a', encoding='utf-8') as file:
        file.write(f'{user}:{password}\n')


class LogVar(tkinter.Variable):

    def __init__(self, root: tkinter.Tk, value: str = None, name: str = None) -> None:
        super().__init__(root, value, name)

    def get(self) -> list:
        """
            Return values as a list.
        """

        return list(self._tk.globalgetvar(self._name))

    def update(self, value: str) -> None:
        """
            Adds the given element to the beginning of the list.
        """

        data = self.get()
        data.insert(0, value)

        self._tk.globalsetvar(self._name, data)
