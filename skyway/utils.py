from rasterio.windows import Window

with rasterio.open(impath) as src:
    plt.figure(figsize=(10, 10))
    arr = src.read(window=Window(512, 512, 512*2, 512*2))
    rashow(arr)
