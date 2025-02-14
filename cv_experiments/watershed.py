'''
Experiment with watershed algorithm, might be a stage in the bee counting ...
'''

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)

img = img[1000:2000, 1000:2000]

assert img is not None, 'Image not found'

img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
sat_max = img[..., 1].max()
img[:, :, 2] = ((img[..., 2]/255)**0.25).clip(0, 1)*255
img[..., 1] = ((img[..., 1]/255)**0.25).clip(0, 1)*255
# img[..., 1].fill(128)

img = cv.cvtColor(img, cv.COLOR_HSV2BGR)
cv.imshow('Saturated', img)
cv.waitKey(0)

cv.destroyAllWindows()

