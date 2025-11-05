import cv2 as cv
import numpy as np
from enum import Enum
import numpy as np
from counting.contour import Contour


class Image:
    type = Enum('Images', [('ORIGINAL', 1),('PREVIOUS',2),('CURRENT',3),('OUTPUT',4)])

    def __init__(self, image_path, settings):
        self.image_path = image_path
        self.settings = settings

        self.image = cv.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not read image from path: {image_path}")

        self.output_image = self.image.copy()

        self.previous_image = self.image.copy()
        self.current_image = self.image.copy()

    def remove_background(self):
        """
        Remove background by detecting the white plate, cropping to its contour, 
        and setting everything outside the contour to white.
        Works on the original image before any other processing.
        """
        # Work with the original image
        original = self.image.copy()
        
        # Convert to grayscale for thresholding
        gray = cv.cvtColor(original, cv.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv.GaussianBlur(gray, (5, 5), 0)
        
        # Threshold to detect the white plate (white plate will be 255, background darker)
        # Using OTSU to automatically find the threshold
        _, thresh = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        
        # Optional: Apply morphology to clean up the threshold
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel, iterations=2)
        thresh = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            print("Warning: No contours found for background removal")
            self.current_image = original
            return
        
        # Find the largest contour (assuming this is the plate)
        plate_contour = max(contours, key=cv.contourArea)
        
        # Create a mask for the plate
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv.drawContours(mask, [plate_contour], -1, 255, -1)  # Fill the contour
        
        # Create white background
        white_background = np.ones_like(original) * 255
        
        # Copy only the plate region to the white background
        result = white_background.copy()
        result[mask == 255] = original[mask == 255]
        
        # Get bounding rectangle to crop
        x, y, w, h = cv.boundingRect(plate_contour)
        
        # Add some padding to the crop (optional)
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(original.shape[1] - x, w + 2 * padding)
        h = min(original.shape[0] - y, h + 2 * padding)
        
        # Crop the result
        cropped = result[y:y+h, x:x+w]
        
        # Update the current image and output image
        self.current_image = cropped
        self.output_image = cropped.copy()
        
        # Also update the original image so subsequent processing uses the cropped version
        self.image = cropped
        self.previous_image = cropped.copy()

    def blur(self):
        self.previous_image = self.current_image.copy()
        self.current_image = cv.GaussianBlur(self.previous_image, self.settings["blur_ksize"], 0)

    def expose_piecewise_std(self):
        self.previous_image = self.current_image.copy()
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

    def threshold(self):
        self.previous_image = self.current_image.copy()
        # # Extract V channel (brightness) from HSV
        # h, s, v = cv.split(self.current_image)
        # v = Image.expose_piecewise_std(v)
        # Apply OTSU threshold on the V channel
        _, thresholded = cv.threshold(self.current_image, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
        self.current_image = thresholded

    def extract_v(self):
        self.previous_image = self.current_image.copy()
        h, s, v = cv.split(self.current_image)
        self.current_image = v

    '''
    function: draw_contours
        Draw contours on the output image. Options for color, thickness, and whether to number contours. 
    inputs: contours - list of Contour class instances as numpy arrays
    outputs: None
    '''
    def draw_contours(self, contours, *, color=(0, 255, 0), thickness=2, bool_number_contours=False):
        """Draw contours on the output image with numbers indicating their index."""

        for c in contours:
            # Draw the contour
            cv.drawContours(self.output_image, [c.contour], -1, color, thickness)

            if not bool_number_contours:
                continue 

            #pos is (x,y) coordinates of centroid
            cx, cy = c.centroid

            # Draw the contour number
            color_text = (255, 0, 0)
            cv.putText(self.output_image, 
                      str(c.id), 
                      (cx-10, cy+10),  # Offset slightly to center the number
                      cv.FONT_HERSHEY_SIMPLEX, 
                      0.8,  # Font scale
                      color_text, 
                      2)   # Thickness

        return self.output_image

    def morphology(self):
        self.previous_image = self.current_image.copy()
        # self.current_image = cv.morphologyEx(self.current_image, cv.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=2)   # was in old code and commented out. Not sure if needed
        self.current_image = cv.morphologyEx(self.current_image, cv.MORPH_CLOSE, np.ones((3,3), np.uint8), iterations=2)
    
    def make_landscape(self):
        self.previous_image = self.current_image.copy()
        if self.current_image.shape[0] > self.current_image.shape[1]:
            self.current_image = cv.rotate(self.previous_image, cv.ROTATE_90_CLOCKWISE)
            self.output_image = self.current_image.copy()

    '''
    function: add_contours
        Draws contours on current image, saving previous image as backup. The function also draws the contour number on top of each contour.
    inputs: contours - list of contours as numpy arrays, as provided by cv2.findContours
    outputs: None
    '''
    def add_contours(self, contours):
        self.previous_image = self.current_image.copy()
        cv.drawContours(self.current_image, contours, -1, (0,255,0), 2)

    def get_image(self, image_type: type):
        if image_type == self.type.ORIGINAL:
            return self.image
        elif image_type == self.type.PREVIOUS:
            return self.previous_image
        elif image_type == self.type.CURRENT:
            return self.current_image
        elif image_type == self.type.OUTPUT:
            return self.output_image
    
    def show_image(self, image_type: type, window_name="Current Image"):
        if image_type == self.type.ORIGINAL:
            img = self.image
        elif image_type == self.type.PREVIOUS:
            img = self.previous_image
        elif image_type == self.type.CURRENT:
            img = self.current_image
        elif image_type == self.type.OUTPUT:
            img = self.output_image

        # img = Image._resize_image(img, height=1080)
        #rotate image 90 degrees clocwise
        # img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)

        cv.imshow(window_name, img)
        cv.waitKey(0)
        cv.destroyAllWindows()
    
    def save_image(self, output_path, image_type: type):
        if image_type == self.type.ORIGINAL:
            img = self.image
        elif image_type == self.type.PREVIOUS:
            img = self.previous_image
        elif image_type == self.type.CURRENT:
            img = self.current_image
        elif image_type == self.type.OUTPUT:
            img = self.output_image

        cv.imwrite(output_path, img)
        print(f"Image saved to {output_path}")


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

    # def expose_piecewise_std(img):
    #     lut = np.arange(256, dtype=np.float32) / 255.0
    #     p1 = 0.4    # < 1
    #     p2 = 2    # < 1 / p1
    #     sep = int(p1 * 255)
    #     lut[0:sep] *= p2
    #     lut[sep:] += lut[sep-1] - lut[sep]
    #     lut = (np.clip(lut, 0, 1) * 255.0).astype(np.uint8)

    #     return cv.LUT(img, lut)