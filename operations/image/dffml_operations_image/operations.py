from typing import List
import cv2
import numpy as np

from dffml.df.base import op


@op
async def flatten(array: List[int]) -> List[int]:
    return np.array(array).flatten()


@op
async def resize(
    src: List[int],
    dsize: List[int],
    fx: float = None,
    fy: float = None,
    interpolation: int = None,
) -> List[int]:
    """
    Resizes image array to the specified new dimensions

    - If the new dimensions are in 2D, the image is converted to grayscale.

    - To enlarge the image (src dimensions < dsize),
        it will resize the image with INTER_CUBIC interpolation.

    - To shrink the image (src dimensions > dsize),
        it will resize the image with INTER_AREA interpolation
    """
    if len(dsize) == 2:
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    else:
        dsize = dsize[:2]
    dsize = tuple(dsize)
    if interpolation is None:
        if dsize > src.shape:
            interpolation = cv2.INTER_CUBIC
        else:
            interpolation = cv2.INTER_AREA

    parameters = {k: v for k, v in locals().items() if v is not None}

    resized_image = cv2.resize(**parameters)
    return resized_image
