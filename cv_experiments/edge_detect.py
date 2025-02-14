'''
Experiment to learn how to edge detect using OpenCV.
Results might also give indication of clumped bees being detectable.
'''

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)
cv.imshow('Original', img)

KERNEL_SIZE = 5
BLUR_SIZE = 5
THRESHOLD1 = 70
THRESHOLD2 = 120

# do gradient magnitude (edge detection)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.GaussianBlur(gray, (5, 5), 0)

edges = cv.Canny(gray, 100, 150)
ret, mask = cv.threshold(edges, THRESHOLD1, THRESHOLD2, cv.THRESH_BINARY)
edges_rgb = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
edges_rgb = edges_rgb * np.array([1, 0, 1], dtype=np.uint8)
mask_inv = cv.bitwise_not(edges)

img_out = cv.bitwise_and(img, img, mask=mask_inv)
img_out = cv.add(img_out, edges_rgb)
cv.imshow('Edges', img_out)

cv.imwrite('outputs/bee-image1-edgepass.png', img_out)

# wait for key press
cv.waitKey(0)
cv.destroyAllWindows()

