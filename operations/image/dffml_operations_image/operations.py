from typing import List
import cv2
import mahotas
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


@op
async def convert_color(src: List[int], code: str,) -> List[int]:
    """
    Converts images from one color space to another
    """
    # TODO Create a mapping of color conversion names to their integer codes.
    # Reference: https://docs.opencv.org/master/d8/d01/group__imgproc__color__conversions.html#ga4e0972be5de079fed4e3a10e24ef5ef0

    code = getattr(cv2, "COLOR_" + code.upper())
    return cv2.cvtColor(src, code)


@op
async def calcHist(
    images: List[int],
    channels: List[int],
    mask: List[int],
    histSize: List[int],
    ranges: List[int],
) -> List[int]:
    """
    Calculates a histogram
    """
    return cv2.calcHist(**locals())


@op
async def HuMoments(m: List[int]) -> List[int]:
    """
    Calculates seven Hu invariants
    """
    # If image is not a single channel image convert it
    if len(m.shape) != 2:
        m = cv2.cvtColor(m, cv2.COLOR_BGR2GRAY)
    m = cv2.moments(m)
    hu_moments = cv2.HuMoments(m).flatten()

    return hu_moments


@op
async def Haralick(
    f: List[int],
    ignore_zeros: bool = False,
    preserve_haralick_bug: bool = False,
    compute_14th_feature: bool = False,
    return_mean: bool = False,
    return_mean_ptp: bool = False,
    use_x_minus_y_variance: bool = False,
    distance: int = 1,
) -> List[int]:
    """
    Computes Haralick texture features
    """
    return mahotas.features.haralick(**locals()).mean(axis=0)


@op
async def normalize(
    src: List[int],
    alpha: int = None,
    beta: int = None,
    norm_type: int = None,
    dtype: int = None,
    mask: List[int] = None,
) -> List[int]:
    """
    Normalizes arrays
    """
    src = src.astype("float")
    dst = np.zeros(src.shape)  # Output image array

    parameters = {k: v for k, v in locals().items() if v is not None}

    cv2.normalize(**parameters)
    return dst
