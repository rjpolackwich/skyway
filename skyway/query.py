import typing_extensions as typing
import dataclasses
import json
import csv
import datetime
import requests

from .base import BaseQuerySettings

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


def _make_case_insensitive(value):
    """Replace the first character of a string by an uppercase-lowercase
    regex.
    Parameters
    ----------
    value : str
        Value (ex: "Residential").
    Returns
    -------
    value : str
        Output value (ex: "[rR]esidential").
    """
    return f'[{ value[0].lower() }{ value[0].upper() }]{ value[1:] }'


def _bbox(lat_min, lon_min, lat_max, lon_max):
    """Format bounding box as a string as expected by the Overpass API."""
    return f'({lat_min},{lon_min},{lat_max},{lon_max})'


def ql_query(bounds, tag, values=None, case_insensitive=False, timeout=25):
    """Build an Overpass QL query.
    Parameters
    ----------
    bounds : tuple
        Bounding box (lat_min, lon_min, lat_max, lon_max).
    tag : str
        OSM tag to query (ex: "highway").
    values : list of str
        List of possible values for the provided OSM tag.
    case_insensitive : bool, optional
        Make the first character of each value case insensitive.
        Defaults to `False`.
    timeout : int, optional
        Overpass timeout. Defaults to 25.
    Returns
    -------
    query : str
        Formatted Overpass QL query.
    """
    bbox = _bbox(*bounds)
    if values:
        if case_insensitive:
            values = [_make_case_insensitive(v) for v in values]
        if len(values) > 1 or case_insensitive:
            query = f'["{ tag }"~"{ "|".join(values) }"]'
        else:
            query = f'["{ tag }"="{ values[0] }"]'
    else:
        query = f'["{ tag }"]'
    return f'[out:json][timeout:{ timeout }]; nwr{ query }{ bbox }; out geom qt;'


class OSMDataQuery():
    def __init__(self, bbox=None):
        self.bbox = bbox
        self._header = BaseQuerySettings(out='json', timeout=60, bbox=bbox)
        self.queries = []

    @property
    def header(self):
        return self._header




