import typing_extensions as typing
import dataclasses
import json
import csv
import datetime
import requests


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


class OSMElement():
    pass


class Node(OSMElement):
    _type = "node"


class Way(OSMElement):
    _type = "way"


class Relation(OSMElement):
    _type = "relation"


@dataclasses.dataclass
class BaseQuery:
    elements: typing.typing.List[OSMElement]
    tags: str


def make_opql_query(aoi,
                    elements=["node", "way", "relation"],
                    osm_tags="railway",
                    tag_vals="rail",
                    fmt="json",
                    timeout=25,
                    overpass_url="http://overpass-api.de/api/interpreter",
                    dry_run=False,
                    ):

    qsmeta = f'[out:{fmt}][timeout:{timeout}];'
    if isinstance(osm_tags, str):
        osm_tags = [osm_tags]*len(elements)
    if isinstance(tag_vals, str):
        tag_vals = [tag_vals]*len(elements)
    qsbody = '('
    for el, tag, val in zip(elements, osm_tags, tag_vals):
        qsbody += f'{el}["{tag}"="{val}"]{aoi};'.replace(' ', '')
    qsbody += ');'
    qsout = 'out;>;out skel qt;'
    qs = qsmeta + qsbody + qsout
    if dry_run:
        return qs

    resp = requests.get(overpass_url, params={'data': qs})
    resp.raise_for_status()
    return resp.json()
