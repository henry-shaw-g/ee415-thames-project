import cv2 as cv
from enum import Enum
import numpy as np



class Contour:
    type = Enum('Contour', [('unprocessed', 1),('rejected',2),('negative',3),('single_bee',4),('clump',5)])

    def __init__(self, contour):

        self.contour = contour #numph array of contour points
        # self.hierarchy = None # hierarchy info from cv.findContours

        self.area = cv.contourArea(contour) # area of the contour

        self.centroid = self.get_centroid() # (x, y) of contour centroid

        self.contour_type = Contour.type.unprocessed

        #bounding box data
        self.bounding_box = cv.boundingRect(contour) # (x, y, w, h) of bounding box
        self.bounding_box_x = self.bounding_box[0]
        self.bounding_box_y = self.bounding_box[1]
        self.bounding_box_w = self.bounding_box[2]
        self.bounding_box_h = self.bounding_box[3]
        self.bounding_box_area = self.bounding_box_w * self.bounding_box_h
        self.bounding_box_aspect_ratio = self.bounding_box_w / self.bounding_box_h if self.bounding_box_h != 0 else 0

        #fitted elipse data
        self.fitted_ellipse = cv.fitEllipse(contour) if len(contour) >= 5 else ((0,0),(0,0),0) # ((x,y),(w,h),theta)
        self.fitted_ellipse_width = self.fitted_ellipse[1][0]
        self.fitted_ellipse_height = self.fitted_ellipse[1][1] 
        self.fitted_ellipse_angle = self.fitted_ellipse[2]
        self.fitted_ellipse_coords = self.fitted_ellipse[0]

        self.fitted_ellipse_area = np.pi * (self.fitted_ellipse_width/2) * (self.fitted_ellipse_height/2)
        self.fitted_ellipse_aspect_ratio = self.fitted_ellipse_width / self.fitted_ellipse_height if self.fitted_ellipse_height != 0 else 0

    def set_type(self, contour_type: type):
        self.contour_type = contour_type
    
    def get_type(self):
        return self.contour_type

    def get_centroid(self):
        M = cv.moments(self.contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        return (cX, cY)