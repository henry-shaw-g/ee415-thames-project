import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

from counting.contour import Contour

class Contours:
    def __init__(self, image_thresholded, settings_counting):
        self.image_thresholded = image_thresholded
        self.settings_counting = settings_counting

        self._find_countours_contours = None 
        self._find_countours_hierarchy = None

        self.contours = []  # list of Contour objects


    def find_contours(self):
        contours, hierarchy = cv.findContours(self.image_thresholded, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        self._find_countours_contours = contours
        self._find_countours_hierarchy = hierarchy

        for cnt in contours:
            contour_obj = Contour(cnt, hierarchy)
            self.contours.append(contour_obj)

        return contours, hierarchy

      


if __name__ == "__main__":

    pass