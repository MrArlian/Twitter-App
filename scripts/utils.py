import tkinter
import typing
import os

from requests import Session, exceptions

import xlwt


DATA_DIR = os.path.join(os.path.split(os.getcwd())[0], 'data')
SESSION = Session()
FIELDS_NAMES = (
    'Name', 'Registration',
    'Followers', 'Tweets'
)


def check_internet() -> bool:
    """
        Сhecks internet connections.
    """

    try:
        SESSION.get('https://twitter.com', timeout=3)
    except (exceptions.ConnectionError, exceptions.ConnectTimeout):
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
        data = [row.rsplit()[0].split(':', 1) for row in raw_data]
    else:
        data = [row.rsplit()[0] for row in raw_data]

    return data


def check_proxy(proxies: typing.Iterable[str]) -> str:
    """
        checks the proxy server for operability.
    """

    for proxy in proxies:
        try:
            SESSION.get('https://twitter.com', proxies={'http': proxy, 'https': proxy}, timeout=3)
            return proxy
        except (exceptions.ConnectTimeout, exceptions.ProxyError):
            pass

    return ''


def write_data(data: typing.Iterable) -> None:
    """
        Сreate excel file with calons: Name, Registration Followers, Tweets.
        It also writes data.
    """

    book = xlwt.Workbook()
    sheet = book.add_sheet('Data')

    for field, col_x in zip(FIELDS_NAMES, range(len(FIELDS_NAMES))):
        sheet.write(0, col_x, field)

    for item, row_x in zip(data, range(2, len(data) + 2)):
        for obj, col_x in zip(item, range(len(item))):
            sheet.write(row_x, col_x, obj)

    book.save(os.path.join(DATA_DIR, 'user_data.xls'))


def write_account(status: str, user: str, password: str) -> None:
    """
        Create a file if it doesn't exist and append "Username: Password" to it.
    """

    with open(os.path.join(DATA_DIR, f'{status}.txt'), 'a', encoding='utf-8') as file:
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
