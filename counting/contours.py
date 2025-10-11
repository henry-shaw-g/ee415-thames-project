import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

from contour import Contour

class Contours:
    def __init__(self, image_thresholded, original_image, settings):
        self.original_image = original_image
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
            contour_obj = Contour(cnt)
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

    def output_contours_to_image(self, output_path):
        import os
        for i, cnt in enumerate(self.contours):
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
            output_file = os.path.join(output_path, f"contour_{i}.png")
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Write the image and check the return value
            success = cv.imwrite(output_file, crop)
            if not success:
                print(f"Failed to write image {output_file}")


    def display_contour_histogram(self):
        # Separate areas by contour type
        single_bee_areas = [c.area for c in self.contours if c.contour_type == Contour.type.single_bee]
        clump_areas = [c.area for c in self.contours if c.contour_type == Contour.type.clump]
        unprocessed_areas = [c.area for c in self.contours if c.contour_type == Contour.type.unprocessed]

        # Calculate appropriate bin range
        all_areas = [c.area for c in self.contours]
        if not all_areas:
            print("No contours to display")
            return
            
        min_area = min(all_areas)
        max_area = max(all_areas)
        
        # Create bins that make sense for your data
        # Assuming single bees are smaller than clumps
        bins = np.linspace(min_area, max_area, 40)
        
        plt.figure(figsize=(12, 6))
        
        # Plot histograms
        if single_bee_areas:
            plt.hist(single_bee_areas, bins=bins, color='green', alpha=0.5, label='Single Bees')
        if clump_areas:
            plt.hist(clump_areas, bins=bins, color='red', alpha=0.5, label='Clumps')
        if unprocessed_areas:
            plt.hist(unprocessed_areas, bins=bins, color='gray', alpha=0.5, label='Unprocessed')
        
        plt.title('Contour Area Distribution')
        plt.xlabel('Area (pixels)')
        plt.ylabel('Frequency')
        plt.legend()
        
        # Add grid for better readability
        plt.grid(True, alpha=0.3)
        
        # Add statistics annotation
        stats_text = f"Total Contours: {len(self.contours)}\n"
        stats_text += f"Single Bees: {len(single_bee_areas)}\n"
        stats_text += f"Clumps: {len(clump_areas)}\n"
        stats_text += f"Unprocessed: {len(unprocessed_areas)}"
        
        plt.annotate(stats_text, xy=(0.02, 0.98), xycoords='axes fraction',
                     verticalalignment='top', fontsize=9,
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":

    pass