'''
Experiment to see how Hough Circle Transform works in OpenCV and if it works at all on
the bees ...
'''

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)
assert img is not None, 'Image not found'

# cv.imshow('Original', img)
# img = cv.medianBlur(img, 5)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.medianBlur(gray, 5)
print("finding circles")
circles = cv.HoughCircles(gray,cv.HOUGH_GRADIENT, 2, minDist=20,param1 = 120,param2=100,minRadius=50,maxRadius=100)
 
circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv.circle(img,(i[0],i[1]),2,(0,0,255),3)

print("showing image")

cv.imshow('detected circles', img)
cv.waitKey(0)
cv.destroyAllWindows()
