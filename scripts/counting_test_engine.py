'''
module: counting_test_engine.py
    Sandbox script to run the algorith, will also add functions here to run the algorithm on a collection of all images
    and automatically generate stats.
'''
import os
import sys
import glob
import cv2 as cv


import counting.algorithm
from counting.algorithm import algorithm
from counting.image import Image
from counting.contour import Contour
from counting import cnn_detect
import utils.dev_image_view
from utils.dev_image_view import show_image

def prompt_yes_no():
    while True:
        response = input("Continue? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def get_test_image_path(override=None):
    if override:
        return override
    input_path = "io/input"
    input_image_path = os.environ.get("BEE_IMAGE_PATH")
    if not input_image_path:
        input_image_path = input_path + "/203-3-1-2(2).png"
    return input_image_path

def test_pipeline():

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
    print("Input image path:", input_image_path)

    cnn_detect.load(cnn_detect.YoloV11SegCNN, path_to_weights = weights_path)
    counting.algorithm.USE_CNN_BEE_DETECTION = True

    output = algorithm(input_image_path, settings_path=None)
    image_handle = output.image_handle
    contours_bees = output.contours

    print(f"Final bee count: {output.bee_count} (single bees: {output.single_bee_count}, clumps: {output.clump_count})")
    
    if False:
        for (image_name, enabled) in Image.snapshots_enabled.items():
            if enabled and image_name in image_handle.images:
                image = image_handle.get_image_named(image_name)
                cv.imshow(f"snapshot: {image_name}", image)
                cv.waitKey(0)
                cv.destroyAllWindows()


    
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.clump), color=(255, 255, 0), bool_count_contours=True, thickness=3, text_scale=0.6)  # Bee clump: Uses cyan color
    # image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.unprocessed), color=(0,255,255), thickness=1)  #unprocessed: Uses yellow color
    # image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.rejected), color=(0,0,255), thickness=1)  # Rejected: Uses red color
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.negative), color=(0, 128, 255), thickness=1)  # negative area: Uses orange color
    
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee, source = "binarized"), color=(0, 255,0), thickness=1, text_scale=0.6)
    image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee, source = "cnn"), bool_number_contours=True, color=(0, 125,0), thickness=1, text_scale=0.6)
    # image_handle.draw_ellipses(contours_bees.get_contours(type = Contour.type.single_bee, source = "binarized"), color=(255,0,0), thickness=1)  # Draw fitted ellipses for binarized single bees
    # image_handle.draw_ellipses(contours_bees.get_contours(type = Contour.type.single_bee, source = "cnn"), color=(255, 200, 0), thickness=1)  # Draw fitted ellipses for cnn single bees
    image_handle.draw_bboxes(contours_bees.get_contours(type = Contour.type.clump), color=(255,0,255), thickness=1, show_id=True)  # Draw bounding boxes for single bees in magenta
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

def test_batch_console_output(glob_pattern):
    utils.dev_image_view.set_backend(utils.dev_image_view.ShowImageMatplotlib)
    weights_path = "data/bee_detect_yolov11seg.pt"
    cnn_detect.load(cnn_detect.YoloV11SegCNN, path_to_weights = weights_path)
    counting.algorithm.USE_CNN_BEE_DETECTION = True

    # run algorithm on all images in the batch
    outputs = []
    file_list = sorted(glob.glob(glob_pattern))
    print("List of images to process:")
    for file_path in file_list:
        print(" - ", file_path)
    if not prompt_yes_no():
        print("Aborting batch processing.")
        return

    for file_path in file_list:
            print("Input image path:", file_path)
            output = algorithm(file_path, settings_path=None)
            image_handle = output.image_handle
            contours_bees = output.contours
            image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.clump), color=(255, 255, 0), bool_count_contours=True, thickness=3, text_scale=0.6)  # Bee clump: Uses cyan color
            # image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.unprocessed), color=(0,255,255), thickness=1)  #unprocessed: Uses yellow color
            # image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.rejected), color=(0,0,255), thickness=1)  # Rejected: Uses red color
            image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.negative), color=(0, 128, 255), thickness=1)  # negative area: Uses orange color
            
            image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee, source = "binarized"), color=(0, 255,0), thickness=1, text_scale=0.6)
            image_handle.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee, source = "cnn"), bool_number_contours=True, color=(0, 125,0), thickness=1, text_scale=0.6)
            # image_handle.draw_ellipses(contours_bees.get_contours(type = Contour.type.single_bee, source = "binarized"), color=(255,0,0), thickness=1)  # Draw fitted ellipses for binarized single bees
            # image_handle.draw_ellipses(contours_bees.get_contours(type = Contour.type.single_bee, source = "cnn"), color=(255, 200, 0), thickness=1)  # Draw fitted ellipses for cnn single bees
            image_handle.draw_bboxes(contours_bees.get_contours(type = Contour.type.clump), color=(255,0,255), thickness=1, show_id=True)  # Draw bounding boxes for single bees in magenta
            show_image(image_handle.get_image(Image.type.OUTPUT))
            print(f"Final bee count: {output.bee_count} (single bees: {output.single_bee_count}, clumps: {output.clump_count})")
            outputs.append((file_path, output))

    # print summary
    print("\nBatch processing summary:")
    for (file_path, output) in outputs:
        print(f"Image: {os.path.basename(file_path)} - Total Bees: {output.bee_count} (Single Bees: {output.single_bee_count}, Clumps: {output.clump_count})")

if __name__ == "__main__":
    test_batch_console_output(
        glob_pattern=r"C:\Users\henry\OneDrive - Washington State University (email.wsu.edu)\WSU\EE4156\Suchting, Zachery's files - 415 Documents\25 Nov 4 Counting Session\401-3-2-2*.png"
        )