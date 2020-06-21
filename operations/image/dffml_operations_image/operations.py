from typing import List
import cv2

from dffml.df.base import op


@op
async def resize(
    data: List[int], old_dim: List[int], new_dim: List[int]
) -> List[int]:
    """
    Resizes image array to the specified new dimensions

    - If the new dimensions are in 2D, the image is converted to grayscale.

    - To enlarge the image (old dimensions < new dimensions),
        it will resize the image with INTER_CUBIC interpolation.

    - To shrink the image (old dimensions > new dimensions),
        it will resize the image with INTER_AREA interpolation
    """
    image = data.reshape(old_dim)
    if len(new_dim) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        new_dim = new_dim[:2]
    if new_dim > old_dim:
        resized_image = cv2.resize(
            image, tuple(new_dim), interpolation=cv2.INTER_CUBIC
        )
    else:
        resized_image = cv2.resize(
            image, tuple(new_dim), interpolation=cv2.INTER_AREA
        )

    return resized_image.flatten()
