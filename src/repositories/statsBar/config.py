import pathlib
from src.utils.image import loadFromRGBToGray

currentPath = pathlib.Path(__file__).parent.resolve()
iconsPath = f'{currentPath}/images/icons'
statsPath = f'{currentPath}/images/stats'
images = {
    'icons': {
        'stop': loadFromRGBToGray(f'{iconsPath}/stop.png')
    },
    'stats': {
        'pz': loadFromRGBToGray(f'{statsPath}/pz.png'),
        'hur': loadFromRGBToGray(f'{statsPath}/hur.png'),
        'poison': loadFromRGBToGray(f'{statsPath}/poison.png')
    }
}