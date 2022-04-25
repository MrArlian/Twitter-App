from urllib import error, request

import tkinter
import typing
import os

import xlwt


DATA_DIR = os.path.join(os.path.split(os.getcwd())[0], 'data')

FIELDS_NAMES = (
    'Name', 'Registration',
    'Followers', 'Tweets'
)

PROXY_INDEX = 0


def check_internet() -> bool:
    """
        Сhecks internet connections.
    """

    try:
        request.urlopen('https://google.com')
    except error.URLError:
        return False
    else:
        return True


def file_parser(path: str) -> typing.List[tuple]:
    """
        Parse file.
    """

    if not isinstance(path, str):
        raise TypeError

    if not path:
        return []

    with open(path, 'r', encoding='utf-8') as file:
        raw_data = file.readlines()

    data = []


    for row in raw_data:
        if row.startswith('http'):
            data.append(row.rsplit()[0])
        else:
            data.append(row.rsplit()[0].split(':', 1))

    return data


def get_proxy(raw: typing.Union[list, tuple]) -> str:
    """
        Returns a proxy of type `host:port`

        Writes the index of the proxy to the temporary variable PROXY_INDEX.
            --So that you can return a new proxy.--
    """

    if not isinstance(raw, (list, tuple)):
        raise TypeError

    global PROXY_INDEX


    if len(raw) < PROXY_INDEX + 1:
        return ''

    PROXY_INDEX += 1
    return ':'.join(raw[PROXY_INDEX - 1])


def write_data(data: typing.Union[list, tuple]) -> None:
    """
        Сreate excel file with calons: Name, Registration Followers, Tweets.
        It also writes data.
    """

    if not isinstance(data, (list, tuple)):
        raise TypeError

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

        if not isinstance(value, str):
            raise TypeError

        data = self.get()
        data.insert(0, value)

        self._tk.globalsetvar(self._name, data)
