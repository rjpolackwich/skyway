from rasterio.windows import Window
import shapely.geometry as geom

with rasterio.open(impath) as src:
    plt.figure(figsize=(10, 10))
    arr = src.read(window=Window(512, 512, 512*2, 512*2))
    rashow(arr)


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


