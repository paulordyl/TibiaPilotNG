# Robust image utilities: avoid hard runtime dependency on numba/cv2; fallback to PIL + numpy
try:
    import cv2
except Exception:
    cv2 = None

try:
    from numba import njit
except Exception:
    # no-op decorator when numba is not available
    def njit(**kwargs):
        def _dec(f):
            return f
        return _dec

import numpy as np
from PIL import Image
from typing import Union
from src.shared.typings import BBox, GrayImage
from src.utils.core import hashit, locate


# TODO: add types
# TODO: add unit tests
def cacheChain(imageList):
    def decorator(_):
        lastX = None
        lastY = None
        lastW = None
        lastH = None
        lastImageHash = None

        def inner(screenshot: GrayImage) -> Union[BBox, None]:
            nonlocal lastX, lastY, lastW, lastH, lastImageHash
            if lastX != None and lastY != None and lastW != None and lastH != None:
                copiedImage = screenshot[lastY:lastY +
                                         lastH, lastX:lastX + lastW]
                copiedImageHash = hashit(copiedImage)
                if copiedImageHash == lastImageHash:
                    return (lastX, lastY, lastW, lastH)
            for image in imageList:
                imagePosition = locate(screenshot, image)
                if imagePosition is not None:
                    (x, y, w, h) = imagePosition
                    lastX = x
                    lastY = y
                    lastW = w
                    lastH = h
                    lastImage = screenshot[lastY:lastY +
                                           lastH, lastX:lastX + lastW]
                    lastImageHash = hashit(lastImage)
                    return (x, y, w, h)
            return None
        return inner
    return decorator


# TODO: add unit tests
@njit(cache=True, fastmath=True)
def convertGraysToBlack(arr: np.ndarray) -> np.ndarray:
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i, j] >= 50 and arr[i, j] <= 100:
                arr[i, j] = 0
    return arr


# TODO: add unit tests
def RGBtoGray(image: np.ndarray) -> GrayImage:
    if cv2 is not None:
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # assume image is numpy array or PIL image
    if isinstance(image, np.ndarray):
        # if shape (h,w,3)
        if len(image.shape) == 3:
            return np.dot(image[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        return image.astype(np.uint8)
    # try PIL
    try:
        pil = Image.fromarray(image)
        return np.array(pil.convert('L'), dtype=np.uint8)
    except Exception:
        return np.array(image, dtype=np.uint8)


# TODO: add unit tests
def loadFromRGBToGray(path: str) -> GrayImage:
    return np.array(RGBtoGray(load(path)), dtype=np.uint8)


# TODO: add unit tests
def save(arr: GrayImage, name: str):
    im = Image.fromarray(arr)
    im.save(name)


# TODO: add unit tests
def crop(image: GrayImage, x: int, y: int, width: int, height: int) -> GrayImage:
    return image[y:y + height, x:x + width]


# TODO: add unit tests
def load(path: str) -> np.ndarray:
    if cv2 is not None:
        return np.array(cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB), dtype=np.uint8)
    # fallback to PIL
    img = Image.open(path).convert('RGB')
    return np.array(img, dtype=np.uint8)
