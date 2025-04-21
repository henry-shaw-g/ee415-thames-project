'''
Helpers for working with (binary) masks.
'''

import numpy as np
import cv2 as cv

'''
input:  img: bgr u8 image to apply overlay
        mask: binary mask to apply overlay to.
        color: color to use for the overlay.
'''
def overlay_mask(img: cv.typing.MatLike, mask: cv.typing.MatLike, color: tuple[int, int, int]) -> cv.typing.MatLike:
    # Convert mask to 3 channels
    # Create a colored overlay
    overlay = np.full_like(img, color, dtype=np.uint8)
    overlay = cv.bitwise_and(overlay, overlay, mask=mask)
    # Blend the overlay with the original image using the mask
    blended = cv.addWeighted(img, 1.0, overlay, 0.5, 0)
    return blended