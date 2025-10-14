import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

from contour import Contour

class Contours:
    def __init__(self, image_thresholded, original_image, settings):
        self.original_image = original_image
        self.image_thresholded = image_thresholded
        self.settings = settings

        self._find_contours_contours = None 
        self._find_contours_hierarchy = None

        self.contours = []  # list of Contour objects


    def find_contours(self):
        contours, hierarchy = cv.findContours(self.image_thresholded, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        self._find_contours_contours = contours
        self._find_contours_hierarchy = hierarchy

        for i, cnt in enumerate(contours):
            contour_obj = Contour(cnt, hierarchy[0][i] if hierarchy is not None else None)
            self.contours.append(contour_obj)

        return contours, hierarchy

    def filter_contours_area(self):
        """Filter contours based on area thresholds and mark rejected ones"""
        #get image dimensions
        img_height, img_width = self.image_thresholded.shape[:2]
        img_area = img_height * img_width

        min_area = img_area * self.settings["min_contour_ratio_of_image"] # e.g. 0.000025 of image area
        max_area = img_area * self.settings["max_contour_ratio_of_image"] # e.g. 0.25 of image area

        for contour in self.contours:
            if not (min_area < contour.area < max_area):
                contour.contour_type = Contour.type.rejected

    def output_contours_to_images(self, output_path):
        import os
        for cnt in self.contours:
            # if contour is rejected skip it
            if cnt.get_type() == Contour.type.rejected:
                continue

            x1 = cnt.bounding_box_x
            x2 = cnt.bounding_box_x + cnt.bounding_box_w
            y1 = cnt.bounding_box_y
            y2 = cnt.bounding_box_y + cnt.bounding_box_h  # Changed to addition

            # Ensure coordinates are within image bounds
            height, width = self.original_image.shape[:2]
            x1 = max(0, min(x1, width))
            x2 = max(0, min(x2, width))
            y1 = max(0, min(y1, height))
            y2 = max(0, min(y2, height))

            # Correct order: y coordinates first, then x coordinates
            crop = self.original_image[y1:y2, x1:x2]

            # Skip if crop is empty
            if crop.size == 0:
                continue

            # Use os.path.join for proper path handling
            output_file = os.path.join(output_path, f"contour_{cnt.id}.png")
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Write the image and check the return value
            success = cv.imwrite(output_file, crop)
            if not success:
                print(f"Failed to write image {output_file}")

    def get_contours(self, *, id=None, type=None):
        #Return all contours if no type or id is specified
        if type is None and id is None:
            return self.contours
        
        #return id if specified
        elif id is not None:
            return self.contours[id]

        #return list of contours of specified type
        elif type is not None:
            return [c for c in self.contours if c.get_type() == type]




if __name__ == "__main__":

    pass