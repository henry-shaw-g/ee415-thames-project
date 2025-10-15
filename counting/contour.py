import cv2 as cv
from enum import Enum
import numpy as np

class Contour:
    type = Enum('Contour', [('unprocessed', 1),('rejected',2),('negative',3),('single_bee',4),('clump',5)])
    id_counter = 0

    def __init__(self, contour, hierarchy=None, source="binarized"):
        self.id = Contour.id_counter
        Contour.id_counter += 1
        self.source = source
        self.contour = contour #numpy array of contour points

        # self.hierarchy = None # hierarchy info from cv.findContours

        self.area = cv.contourArea(self.contour) # area of the contour

        self.centroid = self.get_centroid() # (x, y) of contour centroid

        self.contour_type = Contour.type.unprocessed

        #bounding box data
        self.bounding_box = cv.boundingRect(self.contour) # (x, y, w, h) of bounding box
        self.bounding_box_x = self.bounding_box[0]
        self.bounding_box_y = self.bounding_box[1]
        self.bounding_box_w = self.bounding_box[2]
        self.bounding_box_h = self.bounding_box[3]
        self.bounding_box_area = self.bounding_box_w * self.bounding_box_h
        self.bounding_box_aspect_ratio = self.bounding_box_w / self.bounding_box_h if self.bounding_box_h != 0 else 0

        # instead of using a fitted ellipse, use a rotated rectangle 
        self.fitted_rotated_rect = cv.minAreaRect(self.contour) # ((center_x, center_y), (width, height), angle)
        self.fitted_rect_width = self.fitted_rotated_rect[1][0]
        self.fitted_rect_height = self.fitted_rotated_rect[1][1]
        self.fitted_rect_angle = self.fitted_rotated_rect[2]

        #calculating the ellipse area from the rectangle dimensions
        self.fitted_ellipse_area = np.pi * (self.fitted_rect_width/2) * (self.fitted_rect_height/2)
        self.fitted_rect_aspect_ratio = self.fitted_rect_width / self.fitted_rect_height if self.fitted_rect_height != 0 else 0


        #hierarchy data
        self.hierarchy = hierarchy
        self.hierarchy_Next = hierarchy[0] if hierarchy is not None else None
        self.hierarchy_Prev = hierarchy[1] if hierarchy is not None else None
        self.hierarchy_FirstChild = hierarchy[2] if hierarchy is not None else None
        self.hierarchy_Parent = hierarchy[3] if hierarchy is not None else None

        #color data
        average_color_bgr = None
        average_color_hsv = None

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
    
    def get_average_color(self, image):
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv.drawContours(mask, [self.contour], -1, 255, -1) # fill contour on mask
        mean_val = cv.mean(image, mask=mask) # get mean color within contour
        return mean_val[:3] # return BGR only, ignore alpha if present