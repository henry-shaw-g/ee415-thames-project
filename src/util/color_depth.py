'''
Helpers for manipulating image depth.
'''

import numpy as np

'''
input:  img: pixel image to convert.
notes:
        Assumes float images are in the range [0, 1].
        Can apply to grayscale, color or HSV.
'''
def any_to_u8(img):
    if img.dtype == np.uint8:
        return img
    elif img.dtype == np.uint16:
        return (img / 256).astype(np.uint8)
    elif img.dtype == np.uint32:
        return (img / 65536).astype(np.uint8)
    elif img.dtype == np.float32 or img.dtype == np.float64:
        return (img * 255).astype(np.uint8)
    else:
        raise TypeError(f"Unsupported image type: {img.dtype}")

def any_to_f32(img):
    if img.dtype == np.uint8:
        return img.astype(np.float32) / 255
    elif img.dtype == np.uint16:
        return img.astype(np.float32) / 65535
    elif img.dtype == np.uint32:
        return img.astype(np.float32) / 4294967295
    elif img.dtype == np.float32 or img.dtype == np.float64:
        return img.astype(np.float32)
    else:
        raise TypeError(f"Unsupported image type: {img.dtype}")