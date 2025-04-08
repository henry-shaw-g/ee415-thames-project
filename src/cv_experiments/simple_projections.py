'''
Uses charuco detection but assumes the coplanar markers are in a plane
parallel to the camera plane.
'''

import cv2 as cv
import numpy as np

SQUARE_SIZE = 0.05  # 25 mm

def get_marker_center_simple(marker):
    return np.mean(marker[0], axis=0)

def get_marker_size_simple(marker):
    return np.linalg.norm(marker[0][0] - marker[0][1])

img = cv.imread("image_data/aruco-test-images/testbench1-3.png")

detector_params = cv.aruco.DetectorParameters()
detector_dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
detector = cv.aruco.ArucoDetector()
corners, ids, rejected = detector.detectMarkers(img)

if len(corners) != 2:
    raise ValueError("Expected 2 markers, got {}".format(len(corners)))

m0 = corners[0]
m0_p = get_marker_center_simple(m0)
m0_s = get_marker_size_simple(m0)
m1 = corners[1]
m1_p = get_marker_center_simple(m1)
m1_s = get_marker_size_simple(m1)

img_cpy = img.copy()
cv.aruco.drawDetectedMarkers(img_cpy, corners, ids)
cv.circle(img_cpy, (int(m0_p[0]), int(m0_p[1])), 50, (255, 100, 0), -1)
cv.circle(img_cpy, (int(m1_p[0]), int(m1_p[1])), 50, (255, 100, 0), -1)
cv.imshow("detected markers", img_cpy)

d = np.linalg.norm(m0_p - m1_p)
print("marker0 px size:", m0_s, "marker1 px size:", m1_s)
m_s_avg = (m0_s + m1_s) / 2
print("unitless distance between markers:", d)
print("marker distance in m:", d / m_s_avg * SQUARE_SIZE)

cv.waitKey(0)
cv.destroyAllWindows()
