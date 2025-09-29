import cv2 as cv
from enum import Enum
import numpy as np


Contour_Type = Enum('Images', [('rejected', 1),('unknown',2),('single_bee',3),('clump',4)])

class Contour:
    def __init__(self, contour, hierarchy):
        self.contour = contour #numph array of contour points
        self.hierarchy = hierarchy

        self.area = cv.contourArea(contour) # area of the contour
        
        self.contour_type = Contour_Type.unknown 

        #fitted elipse data
        self.fitted_ellipse = cv.fitEllipse(contour)
        self.fitted_ellipse.width = self.fitted_ellipse[1][0]
        self.fitted_ellipse.height = self.fitted_ellipse[1][1] 
        self.fitted_ellipse_angle = self.fitted_ellipse[2]
        self.fitted_ellipse_coords = self.fitted_ellipse[0]

        self.fitted_ellipse_area = cv.contourArea(cv.ellipse2Poly(self.fitted_ellipse[0:2], self.fitted_ellipse[2]//2, 0, 5))
        self.fitted_ellipse_aspect_ratio = self.fitted_ellipse.width / self.fitted_ellipse.height if self.fitted_ellipse.height != 0 else 0
