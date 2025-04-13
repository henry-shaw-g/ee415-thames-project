'''
authors: Henry Shaw, Connor Clouse, John Pratt
date: 2025-04-08

Module which provides logic to detect the markers. 
This gives information to approximate pixel to world units at the bee plane
and to get an ROI to count bees in.
'''


import numpy as np
import cv2 as cv
import typing

IN_USE_ARUCO_DICT = cv.aruco.DICT_4X4_50

params = cv.aruco.DetectorParameters()
dictionary = cv.aruco.getPredefinedDictionary(IN_USE_ARUCO_DICT)
detector = cv.aruco.ArucoDetector()

class MarkerFindResult:
    source_img: cv.typing.MatLike # hopefully this is a reference rather than a copy
    good: bool # good bool, good boy?
    m_corners: typing.Sequence[typing.Sequence[np.ndarray]]
    m_ids: typing.Sequence[int]

    '''
    Rotation number is n * 90 degrees counter clockwise.
    '''
    def rotate_ids(self, id_rotation_dict):
        pass

    '''
    Returns the top left corner of the top left marker in the image and two vectors
    that describe the top and left edges of the parallelogram.
    '''
    def get_roi_parrallelogram(self) -> tuple[(int, int), (int, int), (int, int)]:
        # x_min = np.min(self.m_corners, axis=1)
        x_min = np.min(self.m_corners[0][0,:,0])
        y_min = np.min(self.m_corners[0][0,:,1])
        x_max = np.max(self.m_corners[0][0,:,0])
        y_max = np.max(self.m_corners[0][0,:,1])

        # return np.array([x_min, y_min]), np.array[(x_max - x_min, 0)], np.array[(0, y_max - y_min)]
        return np.array(((x_min, y_min), (x_max - x_min, 0), (0, y_max - y_min), (x_max, y_max)), dtype=np.int32)

    '''
    Return a binary mask (same convention as in the thresholding algorithm) that can be used to ignore 
    features outside the region of interest.
    '''
    def get_roi_mask(self, parallelogram) -> cv.typing.MatLike:
        mask = np.zeros(self.source_img.shape, dtype=np.uint8)
        line = np.array([parallelogram[0], parallelogram[0] + parallelogram[1], parallelogram[3], parallelogram[0] + parallelogram[2]])
        cv.fillPoly(mask, [line], 1, cv.LINE_AA)
        return mask

'''
gray_img: grayscale image possibly containing the markers
'''
def find_markers(img: cv.typing.MatLike) -> MarkerFindResult:
    corners, ids, _ = detector.detectMarkers(img)
    result = MarkerFindResult()
    result.m_corners = corners if corners is not None else []
    result.m_ids = ids if ids is not None else []
    result.source_img = img
    result.good = len(result.m_corners) == 2 and len(result.m_ids) == 2
    return result
