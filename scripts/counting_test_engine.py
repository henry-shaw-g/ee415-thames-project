'''
module: counting_test_engine.py
    Sandbox script to run the algorith, will also add functions here to run the algorithm on a collection of all images
    and automatically generate stats.
'''

import counting.algorithm
from counting.algorithm import algorithm
from counting.image import Image
from counting.contour import Contour
from counting import cnn_detect

if __name__ == "__main__":
    settings_path = None
    # dir_path =  "/Users/clous/Documents/Bee" # dir_path for connors laptop testing
    input_path =  "io/input" # dir_path for connors desktop testing
    output_path = "io/output"

    weights_path = "data/bee_detect_yolov11seg.pt"

    input_image_path = input_path + "/403-X-1-3.jpg"
    output_image_path = output_path + "/output.jpg"
    output_json_path = output_path + "/output.json"
    output_hierarchy_path = output_path + "/hierarchy.txt"

    cnn_detect.load(cnn_detect.YoloV11SegCNN, path_to_weights = weights_path)
    counting.algorithm.USE_CNN_BEE_DETECTION = True

    output = algorithm(input_image_path, settings_path=None)
    image_handle = output.image_handle
    contours_bees = output.contours
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.unprocessed), bool_number_contours=True, color=(0,255,255))  #unprocessed: Uses yellow color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.rejected), color=(0,0,255))  # Rejected: Uses red color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee), bool_number_contours=True, color=(0, 255,0))  # Single Bee: Uses green color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.negative), bool_number_contours=True, color=(0, 128, 255))  # negative area: Uses orange color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.clump), bool_number_contours=True, color=(255, 255, 0))  # Bee clump: Uses cyan color
    image_handle.show_image(Image.type.OUTPUT)