from typing import Union
from src.shared.typings import BBox, GrayImage
from src.utils.core import cacheObjectPosition, locate
from .config import images

# TODO: add unit tests
# TODO: make perf
@cacheObjectPosition
def getStopIconPosition(screenshot: GrayImage) -> Union[BBox, None]:
    return locate(screenshot, images['icons']['stop'])

def getStatsPz(statsBar: GrayImage) -> bool:
    return bool(locate(statsBar, images['stats']['pz']))

def getStatsHur(statsBar: GrayImage) -> bool:
    return bool(locate(statsBar, images['stats']['hur']))

def getStatsPoison(statsBar: GrayImage) -> bool:
    return bool(locate(statsBar, images['stats']['poison']))
