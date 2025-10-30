import os.path
import json
import pathlib
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

from counting.contour import Contour
from counting.contours import Contours
from counting.image import Image
# import render_output
from utils import file_system

#inputs: Image, settings file path
#outputs: Bee count, image with contours to display on frontend, 
#debug: list of contours in python memory 
'''
function: algorithm
inputs: image path, settings file path
outputs: AlgorithmOutput object
'''
def algorithm(image_path, settings_path = None):
    
    settings = get_settings(settings_path)

    image_bees = Image(image_path, settings)
    if image_bees is None:
        raise ValueError("Image could not be loaded. Check camera or file path.")


    ''' Image Processing Pipeline '''
    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.extract_v() #extract just the V channel
    image_bees.expose_piecewise_std() # Expose the V channel
    image_bees.threshold()    # OTSU thresholding on V channel
    image_bees.morphology()  # maybe not needed, I couldnt see many small holes and they will be taken out in the filter area pass

    ''' Finding Contours '''
    contours_bees = Contours(image_bees.get_image(Image.type.CURRENT), image_bees.get_image(Image.type.ORIGINAL), settings)
    contours_bees.find_contours()

    ''' Filter Reject: very small noise and large contours'''
    contours_bees.filter_contours_area()

    ''' Filter Negatives: based on Hierarchy'''
    contours_bees.calculate_mode_hierarchy()
    contours_bees.filter_negatives()
    # TODO: Maybe further filter negatives based on color
    # TODO: Maybe increase area of negative area using watershed

    ''' Filter Single Bees: based on aspect ratio and ellipse area'''
    # TODO: Maybe change to first pass getting median single bee area, then second pass filtering by aspect ratio and area range around median
    contours_bees.filter_singles_aspect_ratio()
    # contours_bees.contour_area_histogram(contours_bees.get_contours(type=Contour.type.single_bee), bins=50)
    contours_bees.calculate_single_bee_statistics()
    print(f"Single bee area statistics: mean={contours_bees.mean_single_bee_area}, median={contours_bees.median_single_bee_area}, stddev={contours_bees.stddev_single_bee_area}")

    ''' Clumps: filter, subtract negatives, calculate count per contour'''
    contours_bees.unprocessed_to_clumps()

    contours_bees.filter_clumps()
    contours_bees.subtract_negatives_from_clumps()
    contours_bees.calculate_bee_count_per_clump()


    ''' Use CNN to find single bees in clumps '''
    #call detect_in_bbox(self, bbox) to get cnn contours for clumps:
    # TODO:  contours_bees.clumps_to_CNN()

    ''' Final Count '''
    total_bee_count = len(contours_bees.get_contours(type=Contour.type.single_bee))
    for c in contours_bees.get_contours(type=Contour.type.clump):   
        if c.bee_count is not None:
            total_bee_count += c.bee_count

    print(f"Total bee count: {total_bee_count}")

    output = AlgorithmOutput()
    output.image_handle = image_bees
    output.bee_count = 0 # TBD
    output.contours = contours_bees
    return output

def take_picture(webcam_index=0):
    #use opencv to take a picture from the camera
    cap = cv.VideoCapture(webcam_index)
    ret, frame = cap.read()
    if ret != True:
        print("Error: Could not read frame from camera.")
        return None
        
    cap.release()
    return frame

'''
class: AlgorithmOutput
    Pretty much just to specify and hold all outputs of algorithm.
'''
class AlgorithmOutput():
    def __init__(self):
        self.image_handle = None
        self.bee_count = 0
        self.contours = None          # list of contours found in the image, needs to identify clumps
        self.images = {}

    '''
    fn: set
    inputs: dict with keys "bee_count", "output_image", "contours"
    '''
    def set(self, dict):
        # self.bee_count = dict.get("bee_count", 0)
        # self.output_image = dict.get("output_image", None)
        # self.contours = dict.get("contours", [])
        pass

    '''
    fn: store_image
    inputs: name, image: cvmatrix
    '''
    def store_image(self, name, image):
        pass
        
    
'''
function: get_settings
inputs: settings file path
outputs: settings dict
'''
def get_settings(settings_path):
    #read settings file
    if settings_path is None:
        # settings_path = "counting/default_settings.json"
        settings_path = os.path.join(file_system.get_project_dir(), "counting/default_settings.json")

    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    return settings

if __name__ == "__main__":
    pass