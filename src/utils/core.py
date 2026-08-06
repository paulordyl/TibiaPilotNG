# Robust utils.core: tolerate missing native deps and provide safe fallbacks
import hashlib
import numpy as np
from typing import Callable, Union
from src.shared.typings import BBox, GrayImage

# cv2, dxcam and farmhash are optional; provide fallbacks when not available
try:
    import cv2
except Exception:
    cv2 = None

try:
    import dxcam
except Exception:
    dxcam = None

try:
    from farmhash import FarmHash64
except Exception:
    FarmHash64 = None

# if camera available, create it; else None
camera = None
if dxcam is not None:
    try:
        camera = dxcam.create(device_idx=0, output_idx=1, output_color='BGRA')
    except Exception:
        camera = None

latestScreenshot = None


# TODO: add unit tests
def cacheObjectPosition(func: Callable) -> Callable:
    lastX = None
    lastY = None
    lastW = None
    lastH = None
    lastImgHash = None

    def inner(screenshot):
        nonlocal lastX, lastY, lastW, lastH, lastImgHash
        if lastX != None and lastY != None and lastW != None and lastH != None:
            if hashit(screenshot[lastY:lastY + lastH, lastX:lastX + lastW]) == lastImgHash:
                return (lastX, lastY, lastW, lastH)
        res = func(screenshot)
        if res is None:
            return None
        lastX = res[0]
        lastY = res[1]
        lastW = res[2]
        lastH = res[3]
        lastImgHash = hashit(
            screenshot[lastY:lastY + lastH, lastX:lastX + lastW])
        return res
    return inner


# TODO: add unit tests
def hashit(arr: np.ndarray) -> int:
    """Hash a numpy array to a stable integer. Use FarmHash if available, else blake2b fallback."""
    try:
        cont = np.ascontiguousarray(arr)
        b = cont.tobytes()
    except Exception:
        # fallback to bytes of repr
        b = repr(arr).encode('utf-8')
    if FarmHash64 is not None:
        try:
            return FarmHash64(b)
        except Exception:
            pass
    # blake2b 8 bytes -> int
    h = hashlib.blake2b(b, digest_size=8).digest()
    return int.from_bytes(h, 'little')


# locate implementations: prefer cv2; if not available, provide conservative fallbacks
def locate(compareImage: GrayImage, img: GrayImage, confidence: float = 0.85, type=None) -> Union[BBox, None]:
    if cv2 is None:
        # no fast template matching available; return None so caller can fallback
        return None
    if type is None:
        type = cv2.TM_CCOEFF_NORMED
    match = cv2.matchTemplate(compareImage, img, type)
    res = cv2.minMaxLoc(match)
    # res[1] is maxVal when TM_CCOEFF_NORMED
    if res[1] <= confidence:
        return None
    return res[3][0], res[3][1], len(img[0]), len(img)


def locateMultiple(compareImg: GrayImage, img: GrayImage, confidence: float = 0.85) -> Union[BBox, None]:
    if cv2 is None:
        return []
    match = cv2.matchTemplate(compareImg, img, cv2.TM_CCOEFF_NORMED)
    loc = np.where(match >= confidence)
    resultList = []
    for pt in zip(*loc[::-1]):
        resultList.append((pt[0], pt[1], len(compareImg[0]), len(compareImg)))
    return resultList


# getScreenshot: prefer dxcam, else fallback to pyautogui if available
def getScreenshot() -> GrayImage:
    global camera, latestScreenshot
    try:
        if camera is not None:
            screenshot = camera.grab()
            if screenshot is None:
                return latestScreenshot
            if cv2 is not None:
                latestScreenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)
            else:
                # assume screenshot already grayscale or BGRA -> take channel 0
                latestScreenshot = np.asarray(screenshot)[:, :, 0]
            return latestScreenshot
    except Exception:
        pass
    # fallback to pyautogui
    try:
        import pyautogui
        img = pyautogui.screenshot()
        arr = np.array(img.convert('L'))
        latestScreenshot = arr
        return latestScreenshot
    except Exception:
        return latestScreenshot
