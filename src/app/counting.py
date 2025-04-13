'''
Algorithm for counting bees (based on area), filtering contours, and ordering them.
'''
import cv2

'''
INPUT:  img: Any RGB image
OUTPUT: Image with preprocessed effects applied
'''
def image_preprocessing(img, img_scale = 0.5, img_exposure=1.5):
    #resize
    img_preprocessed = cv2.resize(img, None, fx=img_scale, fy=img_scale, interpolation=cv2.INTER_CUBIC)
    #exposure
    img_preprocessed = cv2.convertScaleAbs(img_preprocessed,alpha=img_exposure,beta=0)
    #blur
    img_preprocessed = cv2.GaussianBlur(img_preprocessed, (5, 5), 3)

    return img_preprocessed

''' 
input:  img:    HSV image
        lowerV: lower value 
function: 
    Creates an image threshold based on the brightness value determined in lowerV
    Excludes any brightness between lowerV and 255
return: a threshold image
'''
def image_threshold(img, lowerV=0):
    lower=(0,0,lowerV)
    upper=(255,255,255)
    thresh = cv2.inRange(img,lower,upper)
    
    # we could potentially in the future get two masks and cv2.bitwise_or or cv2.bitwise_and them
    # https://stackoverflow.com/questions/48109650/how-to-detect-two-different-colors-using-cv2-inrange-in-python-opencv
    return thresh


def contour_findContours(imgThresh):
    contours, hierarchy = cv2.findContours(imgThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # in the future put these into a class or some other type of data structure.

    return contours, hierarchy #In the future return one object


def contour_filterContours(contours):
    pass




class CountingResult:
    def __init__(self):
        self.annotated_img = None
        self.count = 666
        self.average_single_bee_area = 420
        self.single_bee_num = 90

class Counting:
    '''
    Instance of counting algorithm.
    TODO: make this more memory friendly when we do live video feed.
    '''

    def __init__(self, img):
        '''
        input img: assumed to be a BGR image
        '''
        self.img = img
        
        self.index = []
        self.hulll

    def count() -> CountingResult:
        return CountingResult()

    def _preprocess(self):
        pass

    def _get_shapes(self):
        pass

    def _filter_single_bees():
        pass

    def _filter_clumps():
        pass

    def _get_count():
        pass

