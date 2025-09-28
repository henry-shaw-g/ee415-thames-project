import cv2 as cv
import numpy as np
from enum import Enum

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

    def blur(self):
        self.previous_image = self.current_image.copy()
        self.current_image = cv.GaussianBlur(self.previous_image, self.settings["blur_ksize"], 0)

    def threshold(self, thresh=127, maxval=255):
        self.previous_image = self.current_image.copy()
        _, self.current_image = cv.threshold(self.previous_image, thresh, maxval, cv.THRESH_BINARY)

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

        img = Image._resize_image(img, height=1080)
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