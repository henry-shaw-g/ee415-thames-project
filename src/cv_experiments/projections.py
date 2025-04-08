'''
Notes for the test images.
Marker size is 25x25 mm.
Dictionary is 4x4_50.
'''

import cv2 as cv
import numpy as np

SQUARE_SIZE = 0.05  # 25 mm
SQUARE_OBJECT_POINTS = np.array([(-0.5, 0.5, 0), (0.5, 0.5, 0), (0.5, -0.5, 0), (-0.5, -0.5, 0)], dtype=np.float32)

pixel_size = 1.885e-6
CAM_MATRIX = np.array([[5.7e2, 0, 2e3], [0, 5.7e2, 1.5e3], [0, 0, 1]], dtype=np.float32) #* pixel_size
CAM_DIST_COEFFS = np.array([6.9e-3, -1.5e-3, -1.2e-4, 1.2e-4, 1.0e-4], dtype=np.float32) #* pixel_size
img = cv.imread("image_data/aruco-test-images/testbench1-3.png")

detector_params = cv.aruco.DetectorParameters()
detector_dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
detector = cv.aruco.ArucoDetector()
corners, ids, rejected = detector.detectMarkers(img)
corners = list(corners)
# rotate one of the markers (i messed up the test images)
print(corners[0], type(corners[0]), corners[0].shape)
corners[0] = np.roll(corners[0], 2, 1)
print(corners[0], type(corners[0]))
corners = tuple(corners)
drawn = cv.aruco.drawDetectedMarkers(img, corners, ids)


#[[ 0.00698257 -0.00150291 -0.00011614  0.00011783  0.00010283]]

# get camera pose based on first marker
if len(corners) > 0:
    tvecs = []

    for marker in corners:
        # is np.eye(3) and np.zeros(5) the ideal pinhole camera?
        _, rvec, tvec =  cv.solvePnP(SQUARE_OBJECT_POINTS, marker, CAM_MATRIX, CAM_DIST_COEFFS, None, None, False, cv.SOLVEPNP_ITERATIVE)
        cv.drawFrameAxes(img, CAM_MATRIX, CAM_DIST_COEFFS, rvec, tvec, 1)
        tvecs.append(tvec)
        print("rvec:")
        print(rvec, rvec.shape)
        print("tvec:")
        print(tvec, tvec.shape)    
    
    dist = np.linalg.norm((tvecs[0] - tvecs[1]))
    print("unitless distance between markers:", dist)
    print("marker distance in m:", dist * SQUARE_SIZE)
else:
    print("No markers detected")

xmax = 0
xmin = img.shape[1]
ymax = 0
ymin = img.shape[0]
for corner in corners:
    for point in corner[0]:
        xmax = max(xmax, point[0])
        xmin = min(xmin, point[0])
        ymax = max(ymax, point[1])
        ymin = min(ymin, point[1])

xmin = max(0, xmin - 10)
xmax = min(img.shape[1], xmax + 10)
ymin = max(0, ymin - 10)
ymax = min(img.shape[0], ymax + 10)

cropped = img
cropped = img[int(ymin):int(ymax), int(xmin):int(xmax)]

cv.imshow("detected markers", cropped)
cv.waitKey(0)
cv.destroyAllWindows()
cv.imwrite("outputs/aruco-test/testbench1-1.png", cropped)