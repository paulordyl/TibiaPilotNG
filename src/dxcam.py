import numpy as np

class Camera:
    def __init__(self, *args, **kwargs):
        pass

    def grab(self):
        # Return a dummy BGRA image (120x120) for tests.
        return np.zeros((120, 120, 4), dtype=np.uint8)


def create(device_idx=0, output_idx=1, output_color='BGRA'):
    return Camera()
