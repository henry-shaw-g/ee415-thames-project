import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

img_bgr = cv.imread('image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)
img_hsv = cv.cvtColor(img_bgr, cv.COLOR_BGR2HSV)

# get and plot histograms of H, S and V
h, s, v = cv.split(img_hsv)
hist_h = cv.calcHist([h], [0], None, [256], [0, 256])
hist_s = cv.calcHist([s], [0], None, [256], [0, 256])
hist_v = cv.calcHist([v], [0], None, [256], [0, 256])

plt.figure()
plt.subplot(3, 1, 1)
plt.plot(hist_h, color='r')
plt.title('Hue')
plt.subplot(3, 1, 2)
plt.plot(hist_s, color='g')
plt.title('Saturation')
plt.subplot(3, 1, 3)
plt.plot(hist_v, color='b')
plt.title('Value')
plt.show()