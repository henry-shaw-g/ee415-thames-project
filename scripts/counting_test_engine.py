'''
module: counting_test_engine.py
    Sandbox script to run the algorith, will also add functions here to run the algorithm on a collection of all images
    and automatically generate stats.
'''
import os

import sys
print(sys.path)

import counting.algorithm
from counting.algorithm import algorithm
from counting.image import Image
from counting.contour import Contour
from counting import cnn_detect
import utils.dev_image_view
from utils.dev_image_view import show_image

def get_test_image_path(override=None):
    if override:
        return override
    input_path = "io/input"
    input_image_path = os.environ.get("BEE_IMAGE_PATH")
    if not input_image_path:
        input_image_path = input_path + "/403-X-1-3.jpg"
    return input_image_path

def test_pipeline():
    import cv2 as cv

    utils.dev_image_view.set_backend(utils.dev_image_view.ShowImageMatplotlib)
    settings_path = None
    # dir_path =  "/Users/clous/Documents/Bee" # dir_path for connors laptop testing
    input_path =  "io/input" # dir_path for connors desktop testing
    output_path = "io/output"

    weights_path = "data/bee_detect_yolov11seg.pt"

    input_image_path = get_test_image_path(override=None)
    # output_image_path = output_path + "/output.jpg"
    # output_json_path = output_path + "/output.json"
    # output_hierarchy_path = output_path + "/hierarchy.txt"

    cnn_detect.load(cnn_detect.YoloV11SegCNN, path_to_weights = weights_path)
    counting.algorithm.USE_CNN_BEE_DETECTION = True

    output = algorithm(input_image_path, settings_path=None)
    image_handle = output.image_handle
    contours_bees = output.contours

    show_numbers = True
    show_counts = True

    image_handle.draw_bboxes(contours_bees.get_contours(type = Contour.type.clump), color=(255,0,255), thickness=1)  # Draw bounding boxes for single bees in magenta
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.clump), bool_count_contours=show_counts, color=(255, 255, 0), thickness=cv.FILLED, text_scale=0.6)  # Bee clump: Uses cyan color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.unprocessed), color=(0,255,255), thickness=1)  #unprocessed: Uses yellow color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.rejected), color=(0,0,255), thickness=1)  # Rejected: Uses red color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.negative), color=(0, 128, 255), thickness=1)  # negative area: Uses orange color
    
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee), bool_number_contours=show_numbers, color=(0, 255,0), thickness=1, text_scale=0.6)  # Single Bee: Uses green color
    
    # image_handle.draw_ellipses(contours_bees.get_contours(type = Contour.type.single_bee), color=(255,0,0), thickness=1)  # Draw fitted ellipses for single bees in blue
    show_image(image_handle.get_image(Image.type.OUTPUT))

def test_pipeline_internals():
    from counting.algorithm import get_settings
    from counting.contours import Contours

    # Test internal functions of the algorithm
    settings = get_settings(None)

    input_image_path = get_test_image_path()
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

if __name__ == "__main__":
    test_pipeline()