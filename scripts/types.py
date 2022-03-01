import typing

from dataclasses import dataclass
from .utils import LogVar


@dataclass
class StartEvent:
    files_path: dict
    action: int
    time: int

    logger: LogVar

    subscription: typing.Optional[bool] = None
    repost: typing.Optional[bool] = None
    like: typing.Optional[bool] = None
