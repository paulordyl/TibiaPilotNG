import numpy as np

def rescale_intensity(image, in_range=(0,255), out_range=(0,255)):
    imin, imax = in_range
    omin, omax = out_range
    arr = np.array(image, dtype=np.float32)
    arr = np.clip(arr, imin, imax)
    # avoid division by zero
    denom = (imax - imin) if (imax - imin) != 0 else 1.0
    scaled = (arr - imin) / denom * (omax - omin) + omin
    return scaled


def equalize_hist(image):
    # simple histogram equalization returning float image in [0,1]
    arr = np.array(image, dtype=np.float32)
    # normalize to 0..1
    if arr.max() > 1.0:
        arr = arr / 255.0
    hist, bins = np.histogram(arr.flatten(), bins=256, range=(0.0, 1.0))
    cdf = hist.cumsum()
    if cdf[-1] == 0:
        return arr
    cdf = (cdf - cdf.min()) / (cdf.ptp() + 1e-9)
    # map through cdf
    inds = np.floor(arr * 255).astype(int)
    inds = np.clip(inds, 0, 255)
    equalized = cdf[inds]
    return equalized
