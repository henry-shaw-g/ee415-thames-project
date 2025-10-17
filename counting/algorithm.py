import os.path
import json
import pathlib
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

from counting.contour import Contour
from counting.contours import Contours
from counting import cnn_detect
from counting.contour_merge import Merger
from counting.image import Image
# import render_output
from utils import file_system

''' Static settings and constants '''
USE_CNN_BEE_DETECTION = False

#inputs: Image, settings file path
#outputs: Bee count, image with contours to display on frontend, 
#debug: list of contours in python memory 
'''
function: algorithm
inputs: image path, settings file path
outputs: AlgorithmOutput object
'''
def algorithm(image_path, settings_path):
    
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
    contours_bees.filter_clumps()
    contours_bees.subtract_negatives_from_clumps()
    contours_bees.calculate_bee_count_per_clump()


    ''' Use CNN to find single bees in clumps '''
    if USE_CNN_BEE_DETECTION:
        # add a flag here to toggle this part of the algorithm if you just want to evaluate conventional algorithm
        cnn = cnn_detect.get() # this gets the currently loaded CNN (MUST BE CURRENTLY LOADED)
        cnn_detector = cnn_detect.CNNDetector(cnn, image_bees.get_image(Image.type.ORIGINAL))
        contours_cnn = Contours.fromContourList(
            image_bees.get_image(Image.type.ORIGINAL),
            cnn_detector.process_contour_list(contours_bees.get_contours()), 
            settings)
        
        # repeat contour methods for cnn contours (ADD MORE AS NEEDED)
        contours_cnn.filter_contours_area()
        contours_cnn.filter_singles_aspect_ratio()

        contours_final_list = contours_bees.get_contours() + contours_cnn.get_contours()
        merger = Merger(image_bees.image, contours_final_list, settings)
        contours_final_list = merger() # this acts on the contours_all table and rejects CNN bees that are likely the same

        contours_bees = Contours.fromContourList(
            image_bees.get_image(Image.type.ORIGINAL),
            contours_final_list, 
            settings)
    
    #call detect_in_bbox(self, bbox) to get cnn contours for clumps:
    

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
    settings_path = None
    # dir_path =  "/Users/clous/Documents/Bee" # dir_path for connors laptop testing
    input_path =  "io/input" # dir_path for connors desktop testing
    output_path = "io/output"

    input_image_path = input_path + "/bee1.jpg"
    output_image_path = output_path + "/output.jpg"
    output_json_path = output_path + "/output.json"
    output_hierarchy_path = output_path + "/hierarchy.txt"

    # algorithm(image_path, settings_path)

    settings = get_settings(settings_path)

    image_bees = Image(input_image_path, settings)
    image_bees.make_landscape()

    # print image dimensions for debug purposes
    img_height, img_width = image_bees.current_image.shape[:2]
    img_area = img_height * img_width
    print(f"Image dimensions: {img_width}x{img_height}, area: {img_area}")

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

    image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.unprocessed), bool_number_contours=True, color=(0,255,255))  #unprocessed: Uses yellow color
    image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.rejected), color=(0,0,255))  # Rejected: Uses red color
    image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee), bool_number_contours=True, color=(0, 255,0))  # Single Bee: Uses green color
    image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.negative), bool_number_contours=True, color=(0, 128, 255))  # negative area: Uses orange color
    image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.clump), bool_number_contours=True, color=(255, 255, 0))  # Bee clump: Uses cyan color

    #draw more contours to visualize filtering steps

    # print(f"(id, area) for single bee contours:")
    # for c in contours_bees.get_contours(type=Contour.type.single_bee):
    #     print(f"({c.id}, {c.area})")

    contours_bees.output_contours_to_images(output_path+"/contours")

    # ------------------------------------JSON OUTPUT-------------------------------------

    # add contour info to list
    contour_list = []
    for c in contours_bees.contours:
        contour_list.append({"id": c.id,
                             "type": c.get_type().name,
                             "centroid": c.centroid,
                             "area": c.area,

                             "fitted_shape": {
                                "width": c.fitted_rect_width,
                                "height": c.fitted_rect_height,
                                "angle": c.fitted_rect_angle,
                                "area": c.fitted_ellipse_area,
                                "aspect_ratio": c.fitted_rect_aspect_ratio
                             },

                             "hierarchy": {
                                "next": int(c.hierarchy[0]) if c.hierarchy is not None else None,
                                "prev": int(c.hierarchy[1]) if c.hierarchy is not None else None,
                                "first_child": int(c.hierarchy[2]) if c.hierarchy is not None else None,
                                "parent": int(c.hierarchy[3]) if c.hierarchy is not None else None
                             },
                             "bee count": c.bee_count, #only for clumps
                             "bee count unrounded": c.bee_count_unrounded, #only for clumps
                             })


    # #sort by area descending
    # contour_list = sorted(contour_list, key=lambda x: x["area"], reverse=True)

    #save contour list to json
    with open(output_json_path, 'w') as f:
        json.dump(contour_list, f, indent=4)
    
    print(f"Contour data saved to {output_json_path}")

    # # Save hierarchy data without truncation
    # with open(output_hierarchy_path, 'w') as f:
    #     # First write the shape of the hierarchy array
    #     f.write(f"Hierarchy Shape: {contours_bees._find_contours_hierarchy.shape}\n\n")
    #     f.write("Hierarchy Data (Next, Previous, First Child, Parent):\n")
    #     # Convert the hierarchy array to a more readable format
    #     for i, item in enumerate(contours_bees._find_contours_hierarchy[0]):
    #         # Each item is [Next, Previous, First_Child, Parent]
    #         f.write(f"Contour {i:3d}: [{item[0]:4d}, {item[1]:4d}, {item[2]:4d}, {item[3]:4d}]\n")

    # print(f"Hierarchy data saved to {output_hierarchy_path}")

    image_bees.save_image(output_image_path, Image.type.OUTPUT)

    pass