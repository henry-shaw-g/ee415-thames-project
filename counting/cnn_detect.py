'''

'''

from contour import Contour, Contour_Type

_loaded_cnn = None

def load():
    _loaded_cnn
    if _loaded_cnn:
        raise RuntimeError("CNNDetect class already loaded for this session.")
    
    _loaded_cnn = CNN()
    return _loaded_cnn


def get():
    if _loaded_cnn is None:
        raise RuntimeError("CNNDetect class has not been loaded for this session. Call cnn_detect.load with the appropriate parameters.")

'''
class: CNN
    Wrapping class for loading data for the CNN (weights and architecture)
'''
class CNN:
    def __init__(self):
        pass

'''
class: CNNDetector
    Logical instance of detecting bees from a single image.
'''
class CNNDetector:
    def __init__(self, cnn, source_image):
        self._cnn = cnn
        self.source_image = source_image
        self.contours = []

    # call this for all clumps w/ in the image
    def detect_in_bbox():
        # find all contours in bounding box of specific image
        # maybe do some initial thresholding
        # save found contours into results data
        pass

    def filter_contours(self, conventional_statistics):
        pass
    