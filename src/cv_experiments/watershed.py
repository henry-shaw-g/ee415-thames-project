'''
Experiment with watershed algorithm, might be a stage in the bee counting ...
'''

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR, )

img = img[1000:2000, 1000:2000]
orig = img.copy()

assert img is not None, 'Image not found'

def hue_only(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # get a a gaussian of the hue around red
    # and apply to the saturation channel
    x = (img[:, :, 0]).astype(np.float32)
    y = (img[:, :, 2]).astype(np.float32)
    # x = (x+90) % 180
    img[:, :, 2] = np.clip(np.exp(-((x - 10)/30)**2) * 128 + (y/2), max=255) #+ np.exp(-((img[:, :, 1] - 180)/30)**2)*255
    # img[:, :, 1] = 255
    # img[:, :, 2] = 255
    img = cv.cvtColor(img, cv.COLOR_HSV2BGR)
    return img

def misc(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img[:, :, 2] = ((img[..., 2]/255)**0.25).clip(0, 1)*255
    img[..., 1] = ((img[..., 1]/255)**0.25).clip(0, 1)*255
    return cv.cvtColor(img, cv.COLOR_HSV2BGR)


img = hue_only(img)

cv.imshow('Original', orig)
cv.imshow('Saturated', img)
cv.waitKey(0)

cv.destroyAllWindows()

