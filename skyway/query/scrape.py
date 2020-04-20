import os
import re
import json
import csv
from tempfile import NamedTemporaryFile
from collections import defaultdict
import requests
import pandas as pd
from bs4 import BeautifulSoup

ti_stat_ep = "https://taginfo.openstreetmap.org/api/4/tag/stats"
ti_list_ep = "https://taginfo.openstreetmap.org/api/4/tags/list"
OSM_FEATURES_URL = "https://wiki.openstreetmap.org/wiki/Map_Features#Primary_features"

def write_url(url, outfile):
    r = requests.get(url)
    with open(outfile, 'w') as f:
        f.write(r.text)


def _tagname_from_header(tag):
    hdr = tag.find_previous("h3")
    return hdr.find_next("span", class_="mw-headline").attrs["id"]


def _itrtable(t):
    for row in t.find_all('tr'):
        yield row


def _parse_tagstr(s, tagname, td):
    for v in s.split(","):
        try:
            t, v = v.split("=")
            if t != tagname.lower():
                continue
        except ValueError:
            if t != tagname.lower():
                continue
        if v != "": td[tagname][t].append([v, "NA"])
    return td


def _rendered_strikethrough(td):
    return td.find('s') is not None


def _parse_table(tbl, tagname, tbld, icols=(0, 1, 3), filter_strikethrough=True):
    for i, row in enumerate(_itrtable(tbl)):
        if i == 0: # Header, we define ours by index
            writing = True
            continue
        tds = row.findChildren('td')
        if len(tds) == 0: # We deal here with filtering unwanted subheadings like attrs
            subhead = row.findChild('span', class_="mw-headline")
            if subhead: # Sometimes it's not a span like in highways
                writing = "attribute" not in subhead['id'].lower()
                if tagname == "Railway" and "Additional_features" == subhead['id']:
                    writing = False
        else:
            if writing:
                if filter_strikethrough:
                    # test either first two elms, have to test both cause osm
                    # wiki is a bag of farts
                    if _rendered_strikethrough(tds[0]) or _rendered_strikethrough(tds[1]):
                        continue
                key, val, desc = (tds[icol].get_text().strip("\n").strip() for icol in icols)
                # Don't write about user defined crap
                if "user" not in val.lower():
                    tbld[tagname][key].append([val, desc])
    return tbld



def scrape_primary_features(url=OSM_FEATURES_URL, use_cache=False):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Get the tables and taglists _above_ the 'Additional Properties' items
    # that tail the data in the doc
    adp = soup.find_all("span", class_="mw-headline", id="Additional_properties").pop()
    # There are two kinds of tables in the doc; taglists which call external
    # javascript and can be identified by their div class, and html tables which
    # can be parsed via row elements. Statistical data much be called manually
    # here using the osm api after the key, value pairs are collected.

    # Get the tags
    tagd = defaultdict(lambda: defaultdict(list))
    tags = adp.find_all_previous('div', class_='taglist')

    tbld = defaultdict(lambda: defaultdict(list))
    tbls = adp.find_all_previous('table', class_='wikitable')
    # To get the correct tagname, look for the span under the previous <h3>
    # element. This groups tags correctly instead of under descriptive
    # categories, eg Places instead of Other Places etc
    for tag in tags:
        tagname = _tagname_from_header(tag)
        datastr = tag.attrs['data-taginfo-taglist-tags']
        tagd = _parse_tagstr(datastr, tagname, tagd)

    # We can get the descriptions and other things from the tables
    for tbl in tbls:
        tagname = _tagname_from_header(tbl)
        tbld = _parse_table(tbl, tagname, tbld)

    return (tagd, tbld)


