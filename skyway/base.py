import typing_extensions as typing
import dataclasses
import json
import csv
import datetime


@dataclasses.dataclass
class BaseQuerySettings:
    out: str
    maxsize: int
    timeout: int
    date: typing.typing.Union[str, datetime.datetime] = None
    bbox: tuple = None

    def __repr__(self):
        msg = list()
        for k, v in dataclasses.asdict(self).items():
            if v is not None:
                msg.append(f'''[{k}:{v}]''')
        return "".join(msg) + ";"







