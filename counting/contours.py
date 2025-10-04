import cv2 as cv
import numpy as np
# import matplotlib.pyplot as plt

import contour

class Contours:
    def __init__(self, image_thresholded, settings):
        self.image_thresholded = image_thresholded
        self.settings = settings

        self._find_countours_contours = None 
        self._find_countours_hierarchy = None

        self.contours = []  # list of Contour objects


    def find_contours(self):
        contours, hierarchy = cv.findContours(self.image_thresholded, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        self._find_countours_contours = contours
        self._find_countours_hierarchy = hierarchy

        for cnt in contours:
            contour_obj = contour.Contour(cnt)
            self.contours.append(contour_obj)

        return contours, hierarchy

    def filter_contours_area(self):
        #get image dimensions
        img_height, img_width = self.image_thresholded.shape[:2]
        img_area = img_height * img_width

        min_area = img_area * self.settings["min_contour_ratio_of_image"] # e.g. 0.000025 of image area
        max_area = img_area * self.settings["max_contour_ratio_of_image"] # e.g. 0.25 of image area

        self.contours = [c for c in self.contours if min_area < c.area < max_area]

if __name__ == "__main__":

    pass