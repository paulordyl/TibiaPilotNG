import numpy as np
try:
    from nptyping import NDArray
except Exception:
    NDArray = None
from typing import Any


Creature = np.dtype([('name', np.str_, 64), ('isBeingAttacked', np.bool_)])
# TODO: fix it
CreatureList = NDArray[Any, Any] if NDArray is not None else Any
