'''
This currently has code for the main counting algorithm. See src/cv_experiments.py for other
experiments and tests.
'''

import cv2
import numpy as np

img = cv2.imread('image_data/bee-image-1.jpg')

cv2.namedWindow('output', cv2.WINDOW_NORMAL)
cv2.createTrackbar('threshold', 'output', 0, 255, lambda x: None)

while True:
    cv2.imshow('output', img)
    cv2.waitKey()
    print("what")