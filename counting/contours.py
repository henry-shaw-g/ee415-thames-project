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

        self.mean_single_bee_area = None
        self.median_single_bee_area = None
        self.stddev_single_bee_area = None

        self.contours = []  # list of Contour objects

    @staticmethod
    def fromContourList(original_image, list, settings):
        contours = Contours(original_image, original_image, settings)
        contours.contours = list
        return contours

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

    def filter_singles(self):
        # Get Settings
        min_aspect_ratio = self.settings["min_fitted_ellipse_aspect_ratio"]
        max_aspect_ratio = self.settings["max_fitted_ellipse_aspect_ratio"]

        """FIRST PASS: Filter single contours based on fitted ellipse aspect ratio"""
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

        """SECOND PASS: Filter single contours based on averages from first pass"""
        # Get single bee statistics from first pass
        if len(single_bee_contours) == 0:
            return
        areas = np.array([c.area for c in single_bee_contours])
        aspect_ratios = np.array([c.fitted_rect_aspect_ratio for c in single_bee_contours])
        ellipse_fit_percent_areas = np.array([abs((c.area - c.fitted_ellipse_area)/c.area) * 100 for c in single_bee_contours])

        mean_area = np.mean(areas)
        mean_aspect_ratio = np.mean(aspect_ratios)
        mean_ellipse_fit_percent_area = np.mean(ellipse_fit_percent_areas)

        # define acceptable area range
        min_area = mean_area * self.settings["single_bee_min_area_multiplier"]
        max_area = mean_area * self.settings["single_bee_max_area_multiplier"] 
        

        # 3 zones: too small, acceptable, make a clump
        #Zone 1: 0 to min_area
        #Zone 2: min_area to max_area
        #Zone 3: > max_area 
        for c in self.contours:
            if c.get_type() == Contour.type.clump or c.get_type() == Contour.type.rejected or c.get_type() == Contour.type.negative:
                continue
            # Zone 1: too small, reject
            if c.area < min_area:
                c.set_type(Contour.type.rejected)
                continue
            # Zone 2: acceptable, keep as single bee
            if min_area <= c.area <= max_area:
                c.set_type(Contour.type.single_bee)
                continue
            # Zone 3: too large, make a clump
            if c.area > max_area:
                # c.set_type(Contour.type.clump)
                continue




    def calculate_single_bee_statistics(self):
        single_bee_areas = [c.area for c in self.contours if c.get_type() == Contour.type.single_bee]
        if len(single_bee_areas) == 0:
            self.mean_single_bee_area = 0
            return

        self.mean_single_bee_area = np.mean(single_bee_areas)
        self.median_single_bee_area = np.median(single_bee_areas)
        self.stddev_single_bee_area = np.std(single_bee_areas)

    def set_single_bee_statistics(self, *, mean_single_bee_area, median_single_bee_area, stddev_single_bee_area):
        self.mean_single_bee_area = mean_single_bee_area
        self.median_single_bee_area = median_single_bee_area
        self.stddev_single_bee_area = stddev_single_bee_area

    def copy_single_bee_statistics(self, other):
        self.mean_single_bee_area = other.mean_single_bee_area
        self.median_single_bee_area = other.median_single_bee_area
        self.stddev_single_bee_area = other.stddev_single_bee_area
    
    def unprocessed_to_clumps(self):
        # TODO: In the future maybe leave these as unprocessed and either
        # Use CNN to detect
        # Or treat unprocessed as clumps in calculate_clump_count_per_contour
        for c in self.contours:
            if c.get_type() == Contour.type.unprocessed:
                c.set_type(Contour.type.clump)
        
    def filter_clumps(self):
        # Filter clumps based on area
        for c in self.contours:
            if c.get_type() != Contour.type.unprocessed:
                continue

            if c.area > self.settings["clump_vs_single_multiplier"] * self.mean_single_bee_area:
                c.set_type(Contour.type.clump)

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

    def output_contours_to_json(self, output_path, *, sorted_by_area=False):
        import json
        contour_list = []
        for c in self.contours:
            contour_list.append({"id": c.id,
                                    "type": c.get_type().name,
                                    "centroid": c.centroid,
                                    "area": c.area,

                                    "fitted_shape": {
                                    "width": c.fitted_rect_width,
                                    "height": c.fitted_rect_height,
                                    "angle": c.fitted_rect_angle,
                                    "area": c.fitted_ellipse_area,
                                    "aspect_ratio": c.fitted_rect_aspect_ratio
                                    },

                                    "hierarchy": {
                                    "next": int(c.hierarchy[0]) if c.hierarchy is not None else None,
                                    "prev": int(c.hierarchy[1]) if c.hierarchy is not None else None,
                                    "first_child": int(c.hierarchy[2]) if c.hierarchy is not None else None,
                                    "parent": int(c.hierarchy[3]) if c.hierarchy is not None else None
                                    },
                                    "bee count": c.bee_count, #only for clumps
                                    "bee count unrounded": c.bee_count_unrounded, #only for clumps
                                    })
            
        # #sort by area descending
        if sorted_by_area:
            contour_list = sorted(contour_list, key=lambda x: x["area"], reverse=True)

        #save contour list to json
        with open(output_path, 'w') as f:
            json.dump(contour_list, f, indent=4)

        print(f"Contour data saved to {output_path}")


    def subtract_negatives_from_clumps(self):
        for c in self.contours:
            if c.get_type() != Contour.type.clump:
                continue
            
            # Check if contour has a child
            if c.hierarchy_FirstChild is not None:
                child_index = c.hierarchy_FirstChild
                while child_index != -1:
                    child_contour = self.contours[child_index]
                    if child_contour.get_type() == Contour.type.negative:
                        c.area -= child_contour.area
                    child_index = child_contour.hierarchy_Next
    
    def calculate_bee_count_per_clump(self):
        for c in self.contours:
            if c.get_type() != Contour.type.clump:
                continue
            
            if self.mean_single_bee_area is None or self.mean_single_bee_area == 0:
                c.bee_count = 0
            else:
                c.bee_count = round(c.area / self.mean_single_bee_area)
                c.bee_count_unrounded = c.area / self.mean_single_bee_area
    
    def clumps_to_CNN(self):
        from counting.cnn_detect import CNNDetector

        for c in self.contours:
            if c.get_type() != Contour.type.clump:
                continue

            bbox = c.bounding_box  # (x, y, w, h)
            CNNDetector.detect_in_bbox(bbox)

    def get_contours(self, *, id=None, type=None, source=None):
        #Return all contours if no type or id is specified
        if type is None and id is None:
            return self.contours
        
        #return id if specified
        elif id is not None:
            return self.contours[id]

        #return list of contours of specified type
        
        elif type is not None or source is not None:
            type_override = type is None
            source_override = source is None
            return [c for c in self.contours if (type_override or c.get_type() == type) and (source_override or c.source == source)]

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