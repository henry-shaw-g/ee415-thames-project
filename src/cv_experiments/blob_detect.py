import numpy as np
import cv2 as cv

img = cv.imread("image_data/bee-image-1.jpg", cv.IMREAD_COLOR_BGR)
assert img is not None, "Image not found"

params = cv.SimpleBlobDetector_Params()

# Set Area filtering parameters 
params.filterByArea = True
params.minArea = 100
  
# Set Circularity filtering parameters 
params.filterByCircularity = True 
params.minCircularity = 0.9
  
# Set Convexity filtering parameters 
params.filterByConvexity = True
params.minConvexity = 0.2
      
# Set inertia filtering parameters 
params.filterByInertia = True
params.minInertiaRatio = 0.01
  
# Create a detector with the parameters 
detector = cv.SimpleBlobDetector_create(params) 
      
# Detect blobs 
keypoints = detector.detect(img) 
  
# Draw blobs on our image as red circles 
blank = np.zeros((1, 1))  
blobs = cv.drawKeypoints(img, keypoints, blank, (0, 0, 255),cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) 

cv.imshow("Blobs", blobs)
cv.waitKey(0)
cv.destroyAllWindows()

