'''
Utility functions for modifying colors in images.
'''

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

_std_gamma_correction = 0.3
_std_gamma_offset = -0.2
_std_gamma_LUT = np.arange(256, dtype=np.float32) / 255.0
_std_gamma_LUT = np.clip(np.power(_std_gamma_LUT + _std_gamma_offset, _std_gamma_correction), 0, 1) * 255.0
_std_gamma_LUT = np.uint8(_std_gamma_LUT)

'''
Expose image using the standard settings with pre-computed LUT.
'''
def expose_std(img):
    return cv.LUT(img, _std_gamma_LUT)

'''
Expose image using input settings. LUT is computed on the fly.
'''
def expose(img, gamma, beta=0.0, alpha=1.0):
    # gamma = 0.3
    # alpha = 1.0
    # beta = -0.2
    lut = np.arange(256, dtype=np.float32) / 255.0
    lut = np.clip(np.power(lut + beta, gamma), 0, 1) * 255.0
    lut = np.uint8(lut)
    
    return cv.LUT(np.uint8(alpha * img), lut)

'''
Trying to emulate what you can do in Gimp.
'''
def expose_piecewise_std(img):
    lut = np.arange(256, dtype=np.float32) / 255.0
    p1 = 0.4    # < 1
    p2 = 2    # < 1 / p1
    sep = int(p1 * 255)
    lut[0:sep] *= p2
    lut[sep:] += lut[sep-1] - lut[sep]
    lut = (np.clip(lut, 0, 1) * 255.0).astype(np.uint8)

    return cv.LUT(img, lut)




def delocalize_brightness(img, r):
    denom = cv.GaussianBlur(img, r, 0)
    img = cv.divide(img, denom, scale=255.0)
    return img

# TESTING

def _test_expose():
    cv.namedWindow('controls', cv.WINDOW_NORMAL)

    img = cv.imread('images/bee-image-samples/bee-image-1.jpg')
    img = cv.resize(img, None, None, fx=0.25, fy=0.25, interpolation=cv.INTER_CUBIC)
    img = cv.GaussianBlur(img, (3, 3), 0)
    img = delocalize_brightness(img, (201, 201))
    cv.imshow('original', img)

    def on_any_trackbar(_):
        gamma = cv.getTrackbarPos('gamma', 'controls') / 100.0
        beta = cv.getTrackbarPos('beta', 'controls') / 100.0 - 0.5
        alpha = cv.getTrackbarPos('alpha', 'controls') / 100.0

        exposed = expose(img, gamma, beta, alpha)
        cv.imshow('img', exposed)

    cv.createTrackbar('gamma', 'controls', 100, 100, on_any_trackbar)
    cv.createTrackbar('beta', 'controls', 50, 100, on_any_trackbar)
    cv.createTrackbar('alpha', 'controls', 100, 100, on_any_trackbar)



    on_any_trackbar(0)
    cv.waitKey()

def _test_delocalize_brightness():
    img = cv.imread('images/bee-image-samples/bee-image-1.jpg')
    img = cv.resize(img, None, None, fx=0.25, fy=0.25, interpolation=cv.INTER_CUBIC)

    cv.imshow('original', img)

    img = cv.GaussianBlur(img, (3, 3), 0)

    delocalized = delocalize_brightness(img, (201, 201))
    cv.imshow('delocalized', delocalized)

    cv.waitKey()

if __name__ == "__main__":
    img = cv.imread('images/bee-image-samples/bee-image-1.jpg')
    img = cv.resize(img, None, None, fx=0.25, fy=0.25, interpolation=cv.INTER_CUBIC)
    img = cv.GaussianBlur(img, (3, 3), 0)

    cv.imshow('original', img)

    exposed = expose_piecewise_std(img)
    cv.imshow('exposed', exposed)
    cv.waitKey(0)