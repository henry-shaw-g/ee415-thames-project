'''
Make conventional Aruco markers for printing.
'''

import cv2
import numpy as np

dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
board = cv2.aruco.GridBoard((1, 2), 100, 50, dict)

ids = [0, 1]
imgs = []
for id in ids:
    img = cv2.aruco.generateImageMarker(dict, id, sidePixels=400,borderBits=1)
    imgs.append(img)

for img in imgs:
    cv2.imshow("output", img)
    cv2.waitKey()

res = cv2.hconcat(imgs)
cv2.imshow("output", res)
cv2.waitKey()

cv2.imwrite("image_data/markers/aurco_6x6_50_01.png", res)