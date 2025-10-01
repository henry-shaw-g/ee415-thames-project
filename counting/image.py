import cv2 as cv
import numpy as np
from enum import Enum
import numpy as np

Image_Type = Enum('Images', [('ORIGINAL', 1),('PREVIOUS',2),('CURRENT',3)])

class Image:
    def __init__(self, image_path, settings):
        self.image_path = image_path
        self.settings = settings

        self.image = cv.imread(image_path)
        self.previous_image = self.image.copy()
        self.current_image = self.image.copy()

    def expose_piecewise_std(self):
        # Create a lookup table for piecewise linear exposure adjustment
        lut = np.arange(256, dtype=np.float32) / 255.0
        p1 = 0.4    # Control point (0 < p1 < 1)
        p2 = 2      # Exposure multiplier for dark regions (p2 > 1)
        sep = int(p1 * 255)
        
        # Apply different exposure levels to dark and bright regions
        lut[0:sep] *= p2  # Increase exposure for dark regions
        lut[sep:] += lut[sep-1] - lut[sep]  # Smoothly transition to bright regions
        
        # Ensure values stay in valid range [0,1] and convert back to uint8
        lut = (np.clip(lut, 0, 1) * 255.0).astype(np.uint8)
        
        # Apply the lookup table to the current image
        self.current_image = cv.LUT(self.current_image, lut)

    def to_hsv(self):
        self.previous_image = self.current_image.copy()
        self.current_image = cv.cvtColor(self.previous_image, cv.COLOR_BGR2HSV)

    def blur(self):
        self.previous_image = self.current_image.copy()
        self.current_image = cv.GaussianBlur(self.previous_image, self.settings["blur_ksize"], 0)

    def threshold(self):
        self.previous_image = self.current_image.copy()
        # Extract V channel (brightness) from HSV
        h, s, v = cv.split(self.current_image)
        # Apply OTSU threshold on the V channel
        _, thresholded = cv.threshold(v, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
        self.current_image = thresholded

    def draw_numbered_contours(self, contours, color=(0, 255, 0), thickness=2):
        """Draw contours on the current image with numbers indicating their index."""
        self.previous_image = self.current_image.copy()
        self.current_image = self.image.copy()
        
        for idx, contour in enumerate(contours):
            # Draw the contour
            cv.drawContours(self.current_image, [contour], -1, color, thickness)
            
            # Get the centroid of the contour to place the number
            M = cv.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
            else:
                # Fallback to bounding box center if moments fail
                x, y, w, h = cv.boundingRect(contour)
                cx = x + w//2
                cy = y + h//2
            
            # Draw the contour number
            color_text = (255, 0, 0)
            cv.putText(self.current_image, 
                      str(idx), 
                      (cx-10, cy+10),  # Offset slightly to center the number
                      cv.FONT_HERSHEY_SIMPLEX, 
                      0.8,  # Font scale
                      color_text, 
                      2)   # Thickness
        
        return self.current_image

    def morphology(self):
        self.previous_image = self.current_image.copy()
        # self.current_image = cv.morphologyEx(self.current_image, cv.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=2)   # was in old code and commented out. Not sure if needed
        self.current_image = cv.morphologyEx(self.current_image, cv.MORPH_CLOSE, np.ones((3,3), np.uint8), iterations=2)

    '''
    function: add_contours
        Draws contours on current image, saving previous image as backup. The function also draws the contour number on top of each contour.
    inputs: contours - list of contours as numpy arrays, as provided by cv2.findContours
    outputs: None
    '''
    def add_contours(self, contours):
        self.previous_image = self.current_image.copy()
        cv.drawContours(self.current_image, contours, -1, (0,255,0), 2)

    def get_image(self, image_type: Image_Type):
        if image_type == Image_Type.ORIGINAL:
            return self.image
        elif image_type == Image_Type.PREVIOUS:
            return self.previous_image
        elif image_type == Image_Type.CURRENT:
            return self.current_image
    
    def show_image(self, image_type: Image_Type, window_name="Current Image"):
        if image_type == Image_Type.ORIGINAL:
            img = self.image
        elif image_type == Image_Type.PREVIOUS:
            img = self.previous_image
        elif image_type == Image_Type.CURRENT:
            img = self.current_image

        # img = Image._resize_image(img, height=1080)
        #rotate image 90 degrees clocwise
        # img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)

        cv.imshow(window_name, img)
        cv.waitKey(0)
        cv.destroyAllWindows()


    # preserves aspect ratio 
    @staticmethod
    def _resize_image(image, width=None, height=None, inter=cv.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv.resize(image, dim, interpolation=inter)