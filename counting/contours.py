import cv2 as cv

class Coutour:
    def __init__(self, image_thresholded, settings_counting):
        self.image_thresholded = image_thresholded
        self.settings_counting = settings_counting

    def find_contours(self):

        contours, hierarchy = cv.findContours(self.image_thresholded, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)


        self.contours = contours
        self.hierarchy = hierarchy
        return contours, hierarchy




if __name__ == "__main__":

    pass