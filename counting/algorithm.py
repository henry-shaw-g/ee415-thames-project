import os.path
import json
import pathlib
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

from counting.contour import Contour
from counting.contours import Contours
from counting.cnn_contours import CNNContours
# from counting.contour_merge import Merger
from counting.image import Image
# import render_output
from utils import file_system

''' Static settings and constants '''
USE_CNN_BEE_DETECTION = True

if USE_CNN_BEE_DETECTION:
    import counting.cnn_detect as cnn_detect

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
    image_bees.remove_background()
    image_bees.expose_piecewise_std() # expose all channels
    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.extract_v() #extract just the V channel
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

    ''' Clumps: filter, subtract negatives'''
    # contours_bees.unprocessed_to_clumps()
    # contours_bees.filter_clumps()
    # contours_bees.subtract_negatives_from_clumps()

    ''' Use CNN to find single bees in clumps '''
    if USE_CNN_BEE_DETECTION:
        # add a flag here to toggle this part of the algorithm if you just want to evaluate conventional algorithm
        cnn = cnn_detect.get() # this gets the currently loaded CNN (MUST BE CURRENTLY LOADED)
        cnn_detector = cnn_detect.CNNDetector(cnn, image_bees.get_image(Image.type.ORIGINAL))
        cnn_detections = cnn_detector.process_by_tiles()
        cnn_contours = CNNContours(
            image_bees.get_image(Image.type.CURRENT),
            image_bees.get_image(Image.type.ORIGINAL),
            settings,
            prior_contours=contours_bees,
            cnn_contour_list=cnn_detections,
        )
        # filter CNN detections
        cnn_contours.filter_contours_area()
        cnn_contours.filter_singles_aspect_ratio()
        cnn_contours.merge_cnn_contours()

        contours_bees = cnn_contours
        contours_bees.calculate_single_bee_statistics()

        # for debugging
        cnn_detector.debug_draw_tiles(image_bees.get_image(Image.type.OUTPUT))
    
        image_bees.erase_contours_from_binary(contours_bees.get_contours(), type_include_filter=Contour.type.single_bee)
        contours_clumps = Contours(
            image_bees.get_image(Image.type.CURRENT),
            image_bees.get_image(Image.type.ORIGINAL),
            settings)
        
        contours_clumps.find_contours()
        contours_clumps.copy_single_bee_statistics(contours_bees)
        contours_clumps.filter_contours_area()
        contours_clumps.calculate_mode_hierarchy()
        contours_clumps.filter_negatives()
        contours_clumps.unprocessed_to_clumps()
        contours_clumps.filter_clumps()
        contours_clumps.subtract_negatives_from_clumps()
        contours_clumps.calculate_bee_count_per_clump()

        contours_bees.contours.extend(contours_clumps.contours)
    else:
        # contours_bees.unprocessed_to_clumps()
        contours_bees.filter_clumps()
        contours_bees.subtract_negatives_from_clumps()
        contours_bees.calculate_bee_count_per_clump()

    #call detect_in_bbox(self, bbox) to get cnn contours for clumps:
    

    ''' Final Count '''
    contours_bees.calculate_bee_count_per_clump()
    single_bee_count = len(contours_bees.get_contours(type=Contour.type.single_bee))
    # single_bee_count already computed above
    # clump_count = len(contours_bees.get_contours(type=Contour.type.clump))
    clump_bee_count = 0
    for c in contours_clumps.get_contours(type=Contour.type.clump):
        if getattr(c, "bee_count", None) is not None:
            clump_bee_count += c.bee_count

    total_bee_count = single_bee_count + clump_bee_count

    print(f"Total bee count: {total_bee_count}")

    output = AlgorithmOutput()
    output.image_handle = image_bees
    output.single_bee_count = single_bee_count
    output.clump_count = clump_bee_count
    output.bee_count = total_bee_count # TBD
    output.contours = contours_bees
    return output


'''
class: AlgorithmOutput
    Pretty much just to specify and hold all outputs of algorithm.
'''
class AlgorithmOutput():
    def __init__(self):
        self.image_handle = None
        self.single_bee_count = 0
        self.clump_count = 0
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