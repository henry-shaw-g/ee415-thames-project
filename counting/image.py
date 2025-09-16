import cv2 as cv


class Image:
    def __init__(self, image_path, settings_counting):
        self.image_path = image_path
        self.settings_counting = settings_counting

        self.image = cv.imread(image_path)
        self.image_blurred = None
        self.image_thresholded = None

    def blur(self, ksize=(5, 5)):
        self.image_blurred = cv.GaussianBlur(self.image, ksize, 0)

    def threshold(self, thresh=127, maxval=255):
        if self.image_blurred is None:
            raise ValueError("Image must be blurred before thresholding.")
        _, self.image_thresholded = cv.threshold(self.image_blurred, thresh, maxval, cv.THRESH_BINARY)


    