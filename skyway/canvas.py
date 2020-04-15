import os
import sys
import typing_extensions as typing
import json
import math
import datetime
from functools import partial, partialmethod
import types
import dataclasses
from pathlib import Path

import boto3
import botocore
import s3fs

import numpy as np
import networkx as nx
import rasterio
from rasterio.plot import show as rashow
import shapely.ops as ops
import shapely.geometry as geom
from pyproj import CRS, Proj, Transformer

import tiletanic as tt
import canvas

WORLD_CRS = CRS.from_epsg(4326)
MAP_CRS = CRS.from_epsg(3857)


# Bounds are always (lonmin, latmin, lonmax, latmax) from shit
# eg (xmin, ymin, xmax, ymax)

class GeoTileTransformer(object):
    def __init__(self, tile, to_crs):
        self.tile = tile
        self.to_crs = to_crs

    def __enter__(self):
        self.tile.set_crs(self.to_crs)
        return self.tile

    def __exit__(self, *args):
        self.tile.reset_crs()



class WGS84Transformer(GeoTileTransformer):
    def __init__(self, tile):
        GeoTileTransformer.__init__(self, tile, WORLD_CRS)



class GeoTile(object):
    dtype = [('ix', int), ('iy', int), ('zoom', int)]

    def __init__(self, xi, yi, zoom, tiler=None):
        self.xi = xi
        self.yi = yi
        self.zoom = zoom
        self._tiler = tiler
        self._qk = None
        if self.quadkey[0] in ('0', '1'):
            self.__crs__ = tiler._crs_n
            self._tr = tiler._tr_n
        else:
            self.__crs__ = tiler._crs_s
            self._tr = tiler._tr_s
        self._crs = self.__crs__
        self.__gi__ = geom.box(*self.utm_bounds).__geo_interface__
        self._gi = self.__gi__

    @property
    def utm_zone(self):
        return self._tiler.utm_zone

    def parent(self):
        return self._tiler.tile_parent(self.asTile)

    def children(self):
        return self._tiler.tile_children(self.asTile)

    @property
    def quadkey(self):
        if self._qk is None:
            self._qk = self._tiler.quadkey_from_tile(self.asTile)
        return self._qk

    @property
    def asTile(self):
        return tt.base.Tile(self.xi, self.yi, self.zoom)

    @property
    def crs(self):
        return self._crs

    def set_crs(self, to_crs):
        ccrs = self._crs
        self._crs = to_crs
        if ccrs == to_crs:
            return
        if ccrs == self.__crs__ and to_crs == WORLD_CRS:
            tr = self._tr
        else:
            tr = Transform.from_crs(ccrs, to_crs, always_xy=True).transform
        self._gi = ops.transform(tr, geom.shape(self)).__geo_interface__

    toWGS84 = partialmethod(set_crs, WORLD_CRS)

    def reset_crs(self):
        self._crs = self.__crs__
        self._gi = self.__gi__

    @property
    def width_meters(self):
        return self._tiler.tile_size_at_zoom(self.zoom)

    @property
    def length_meters(self):
        return self.width_meters

    @property
    def utm_bounds(self):
        return self._tiler._tiler.bbox(self.asTile)

    @property
    def bounds(self):
        return geom.shape(self).bounds

    @property
    def __geo_interface__(self):
        return self._gi

    @classmethod
    def _from_tile(cls, tile, tiler=None):
        return cls(tile.x, tile.y, tile.z, tiler=tiler)

    @property
    def asShape(self):
        return geom.asShape(self)

    @property
    def z(self):
        return self.zoom

    def __iter__(self):
        return iter([self.xi, self.yi, self.zoom])





class ProjectedUTMTiling(object):

    def __init__(self, zone=None, tiler=None):
        self.utm_zone = zone
        self._tiler = tiler
        self._tiling_zoom_level = tiler.zoom
        self._tiling_physical_length = tiler.tile_size
        self._tf = partial(GeoTile._from_tile, tiler=self)
        self._crs_n = CRS.from_epsg(f'326{self.utm_zone:02d}')
        self._crs_s = CRS.from_epsg(f'327{self.utm_zone:02d}')
        self._tr_n = Transformer.from_crs(self._crs_n, WORLD_CRS, always_xy=True).transform
        self._tr_s = Transformer.from_crs(self._crs_s, WORLD_CRS, always_xy=True).transform

    def tile_from_xy(self, xcoord, ycoord, zoom=12):
        tile = self._tiler.tile(xcoord, ycoord, zoom)
        return self._tf(tile)

    def tile_from_quadkey(self, qk):
        tile = self._tiler.quadkey_to_tile(qk)
        return self._tf(tile)

    def quadkey_from_tile(self, *tile):
        return self._tiler.quadkey(*tile)

    def tile_parent(self, *tile):
        tile = self._tiler.parent(*tile)
        return self._tf(tile)

    def tile_children(self, *tile):
        children = self._tiler.children(*tile)
        return [self._tf(tile) for tile in children]

    def tile_length_at_zoom(self, zoom_level):
        return self._tiling_physical_length / 2**(zoom_level - self._tiling_zoom_level)

    def zoom_from_tile_dim(self, dimension):
        pass

    def __getattr__(self, atr):
        return getattr(self._tiler, atr)

    def dims_from_zoom(self, zoom, init_dim=16384, init_zoom=12):
        return init_dim / 2**(zoom - init_zoom)



# Accessor api


class CanvasClient(object):
    def __init__(self, bucket, local=True, s3conn=None):
        self.bucket = bucket
        self.local = local
        if not local:
            if s3conn is None:
                s3conn = s3fs.S3FileSystem(anon=False)
        self.s3conn = s3conn

    def list_dir(self, *args, **kwargs):
        if self.local:
            return os.listdir(*args, **kwargs)
        return self.s3conn.ls(*args, **kwargs)




def itrreduce(fn, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = fn([value, element])
    return value


def to_gjson(tile):
    geodata = geom.mapping(t)
    gj = {"type": "Feature",
         "properties": {"tile_id": "+".join([str(t.utm_zone), t.quadkey]),
                        "ix": t.xi,
                        "iy": t.yi,
                        "zoom": t.zoom},
         "geometry": geodata}
    return gj


class CanvasZone(CanvasClient):

    def __init__(self, utm_zone, tiler=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.utm_zone = utm_zone
        self.tiler = ProjectedUTMTiling(zone=utm_zone, tiler=tiler)
        self.cvg = nx.Graph(store=self.bucket, utm_zone=utm_zone)
        self.qk_path = os.path.join(self.bucket, str(utm_zone))
        self._tile_quadkeys_fetched = False
        self._tile_cogs_fetched = False
        self._qksample = self.tile_quadkeys[0]
        self._gtm = None
        self.__gi__ = None

    @property
    def tile_quadkeys(self):
        if not self._tile_quadkeys_fetched:
            qk_paths = self.list_dir(self.qk_path)
            for qkp in qk_paths:
                qk = Path(qkp).parts[-1]
                self.cvg.add_node(qk, obj="quadkey")
            self._tile_quadkeys_fetched = True
        return [n for n in self.cvg.nodes() if self.cvg.nodes[n]['obj'] == "quadkey"]

    @property
    def tile_cogs(self):
        if not self._tile_cogs_fetched:
            for qk in self.tile_quadkeys:
                cog_path = os.path.join(self.qk_path, qk)
                cog_files = self.list_dir(cog_path)
                for fp in cog_files:
                    catid = Path(fp).stem.split("-")[0]
                    self.cvg.add_node(catid, obj="catalog_id")
                    self.cvg.add_edge(catid, qk)
            self._tile_cogs_fetched = True
        return [n for n in self.cvg.nodes() if self.cvg.nodes[n]['obj'] == 'catalog_id']

    @property
    def nqks(self):
        return len(self.tile_quadkeys)

    @property
    def ncatids(self):
        return len(self.tile_cogs)

    @property
    def area_coverage(self, units='m'):
        return str((5_000 * 5_000) * self.nqks) + ' ' + units + '^2'

    def __getitem__(self, quadkey):
        if quadkey not in self.tile_quadkeys:
            raise KeyError
        return self.tiler.tile_from_quadkey(quadkey)

    def __setitem__(self, item):
        raise NotImeplementedError

    def __iter__(self):
        tiles = np.array([self.tiler._tiler.quadkey_to_tile(qk)
                          for qk in self.tile_quadkeys], dtype=GeoTile.dtype)
        for tile in np.sort(tiles, order=['iy', 'ix']):
            yield self.tiler._tf(tt.base.Tile(*tile))

    def iter_geoms(self):
        for tile in iter(self):
            with WGS84Transformer(tile) as geotile:
                yield geotile.asShape

    @property
    def __geo_interface__(self):
        if self.__gi__ is None:
            self.__gi__ = itrreduce(ops.unary_union,
                                    self.iter_geoms()).__geo_interface__
        return self.__gi__

    @property
    def asShape(self):
        return geom.asShape(self)

    @property
    def centroid(self):
        return self.asShape.centroid



class CanvasCollection(CanvasClient):
    def __init__(self, aoi=None, tilescheme=tt.tileschemes.WNUTM5kmTiling, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aoi = aoi
        self.tiler = tilescheme()
        self._zlut = dict()
        self._zone_paths_fetched = False

    def canvas_zones(self):
        if not self._zone_paths_fetched:
            self._zone_paths = self.list_dir(self.bucket)
            self._zone_paths_fetched = True
            self.zones = sorted([int(Path(zp).parts[-1]) for zp in self._zone_paths if Path(zp).parts[-1] not in ('models', 'output')])
        return self.zones

    def zone(self, zone, *args, **kwargs):
        if zone not in self.canvas_zones():
            raise OSError("Zone {} not in path".format(zone))
        if zone in self._zlut: return self._zlut[zone]
        self._zlut[zone] = CanvasZone(zone, bucket=self.bucket, local=self.local, s3conn=self.s3conn, tiler=self.tiler, **kwargs)
        return self._zlut[zone]

    def descriptions(self):
        for z in self.canvas_zones():
            print(z)
            print("Total data area covered: " + self.zone(z).area_coverage)
            print("Total number of quadkey zones: " + str(self.zone(z).nqks))
            print("Total number of catalog ids tiled: " + str(self.zone(z).ncatids))
            print("\n")

