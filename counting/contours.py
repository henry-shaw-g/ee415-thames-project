import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

from counting.contour import Contour

class Contours:
    def __init__(self, image_thresholded, original_image, settings):
        self.original_image = original_image
        self.image_thresholded = image_thresholded
        self.settings = settings

        self._find_contours_contours = None 
        self._find_contours_hierarchy = None

        self.mode_hierarchy = None

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
    
    def filter_negatives(self):
        """Filter negative contours based on hierarchy"""
        for c in self.contours:
            if c.get_type() is not Contour.type.unprocessed:
                continue
            
            # if contours parent is not mode_hierarchy, then its inside another contour, mark as negative
            if c.hierarchy_Parent != self.mode_hierarchy:
                c.set_type(Contour.type.negative)

    def filter_singles_aspect_ratio(self):
        """Filter single contours based on fitted ellipse aspect ratio"""
        min_aspect_ratio = self.settings["min_fitted_ellipse_aspect_ratio"]
        max_aspect_ratio = self.settings["max_fitted_ellipse_aspect_ratio"]
        single_bee_contours = []
        #first pass: broad detection using aspect ratio and ellipse area comparison 
        #(detects almost all single bees, but some clumps, negative area, and noise contours)
        for contour in self.contours:
            if contour.get_type() is not Contour.type.unprocessed:
                continue
            
            aspect_ratio = contour.fitted_rect_aspect_ratio
            if not (aspect_ratio >= min_aspect_ratio and aspect_ratio <= max_aspect_ratio):
                continue

            if abs((contour.area - contour.fitted_ellipse_area)/contour.area) * 100 > self.settings["max_fitted_ellipse_percent_area"]:
                continue
            
            contour.set_type(Contour.type.single_bee)
            single_bee_contours.append(contour)

        # second pass: even stricter filtering using statistical area
        # either Z-score 3-sigma rule or 1.5*IQR rule

        #testing 1.5IQR rule
        areas = np.array([c.area for c in single_bee_contours])
        if areas.size == 0:
            return

        q1 = np.percentile(areas, 25)
        q3 = np.percentile(areas, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        for c in single_bee_contours:
            if not (lower_bound < c.area < upper_bound):
                c.set_type(Contour.type.unprocessed)


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
    
    def calculate_mode_hierarchy(self):
        # get hierarchy parent for top 25% of contours by area
        sorted_contours = sorted(self.contours, key=lambda c: c.area, reverse=True)
        top_25_percent = sorted_contours[:len(sorted_contours) // 4]
        hierarchy_list = [c.hierarchy_Parent for c in top_25_percent]

        self.mode_hierarchy = max(set(hierarchy_list), key=hierarchy_list.count) if hierarchy_list else None
        return self.mode_hierarchy
    
    @staticmethod
    def contour_area_histogram(contours, bins=30):
        areas = [c.area for c in contours]
        plt.hist(areas, bins=bins)
        plt.title("Contour Area Histogram")
        plt.xlabel("Area")
        plt.ylabel("Frequency")
        plt.show()



if __name__ == "__main__":

    pass