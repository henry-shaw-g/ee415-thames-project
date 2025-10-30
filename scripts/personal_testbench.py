import os.path
import json
import pathlib
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

from counting.contour import Contour
from counting.contours import Contours
from counting.image import Image
from counting.algorithm import *

# import render_output
from utils import file_system

if __name__ == "__main__":
    input_path =  "io/input" 
    output_path = "io/output"

    input_image_path = input_path + "/bee1.jpg"
    output_image_path = output_path + "/output.jpg"
    output_json_path = output_path + "/output.json"
    output_hierarchy_path = output_path + "/hierarchy.txt"

    output = algorithm(input_image_path)

    image_handle = output.image_handle
    bee_count = output.bee_count
    contours = output.contours
    print(f"Detected bee count: {bee_count}")


    image_handle.draw_contours(contours.get_contours(type = Contour.type.unprocessed), bool_number_contours=True, color=(0,255,255))  #unprocessed: Uses yellow color
    image_handle.draw_contours(contours.get_contours(type = Contour.type.rejected), color=(0,0,255))  # Rejected: Uses red color
    image_handle.draw_contours(contours.get_contours(type = Contour.type.single_bee), bool_number_contours=True, color=(0, 255,0))  # Single Bee: Uses green color
    image_handle.draw_contours(contours.get_contours(type = Contour.type.negative), bool_number_contours=True, color=(0, 128, 255))  # negative area: Uses orange color
    image_handle.draw_contours(contours.get_contours(type = Contour.type.clump), bool_number_contours=True, color=(255, 255, 0))  # Bee clump: Uses cyan color

    image_handle.save_image(output_image_path, Image.type.OUTPUT)
    print(f"Output image saved to {output_image_path}")




# def old_tb():
#     settings_path = None
#     # dir_path =  "/Users/clous/Documents/Bee" # dir_path for connors laptop testing
#     input_path =  "io/input" # dir_path for connors desktop testing
#     output_path = "io/output"

#     input_image_path = input_path + "/bee1.jpg"
#     output_image_path = output_path + "/output.jpg"
#     output_json_path = output_path + "/output.json"
#     output_hierarchy_path = output_path + "/hierarchy.txt"

#     settings = counting.algorithm.get_settings(settings_path)

#     image_bees = Image(input_image_path, settings)
#     image_bees.make_landscape()

#     # print image dimensions for debug purposes
#     img_height, img_width = image_bees.current_image.shape[:2]
#     img_area = img_height * img_width
#     print(f"Image dimensions: {img_width}x{img_height}, area: {img_area}")

#     ''' Image Processing Pipeline '''
#     image_bees.blur()
#     image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
#     image_bees.extract_v() #extract just the V channel
#     image_bees.expose_piecewise_std() # Expose the V channel
#     image_bees.threshold()    # OTSU thresholding on V channel
#     image_bees.morphology()  # maybe not needed, I couldnt see many small holes and they will be taken out in the filter area pass

#     ''' Finding Contours '''
#     contours_bees = Contours(image_bees.get_image(Image.type.CURRENT), image_bees.get_image(Image.type.ORIGINAL), settings)
#     contours_bees.find_contours()

#     ''' Filter Reject: very small noise and large contours'''
#     contours_bees.filter_contours_area()

#     ''' Filter Negatives: based on Hierarchy'''
#     contours_bees.calculate_mode_hierarchy()
#     contours_bees.filter_negatives()
#     # TODO: Maybe further filter negatives based on color
#     # TODO: Maybe increase area of negative area using watershed

#     ''' Filter Single Bees: based on aspect ratio and ellipse area'''
#     # TODO: Maybe change to first pass getting median single bee area, then second pass filtering by aspect ratio and area range around median
#     contours_bees.filter_singles_aspect_ratio()
#     # contours_bees.contour_area_histogram(contours_bees.get_contours(type=Contour.type.single_bee), bins=50)
#     contours_bees.calculate_single_bee_statistics()
#     print(f"Single bee area statistics: mean={contours_bees.mean_single_bee_area}, median={contours_bees.median_single_bee_area}, stddev={contours_bees.stddev_single_bee_area}")

#     ''' Clumps: filter, subtract negatives, calculate count per contour'''
#     contours_bees.filter_clumps()
#     contours_bees.subtract_negatives_from_clumps()
#     contours_bees.calculate_bee_count_per_clump()


#     ''' Use CNN to find single bees in clumps '''
#     #call detect_in_bbox(self, bbox) to get cnn contours for clumps:
#     # TODO:  contours_bees.clumps_to_CNN()

#     ''' Final Count '''
#     total_bee_count = len(contours_bees.get_contours(type=Contour.type.single_bee))
#     for c in contours_bees.get_contours(type=Contour.type.clump):   
#         if c.bee_count is not None:
#             total_bee_count += c.bee_count

#     print(f"Total bee count: {total_bee_count}")

#     image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.unprocessed), bool_number_contours=True, color=(0,255,255))  #unprocessed: Uses yellow color
#     image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.rejected), color=(0,0,255))  # Rejected: Uses red color
#     image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.single_bee), bool_number_contours=True, color=(0, 255,0))  # Single Bee: Uses green color
#     image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.negative), bool_number_contours=True, color=(0, 128, 255))  # negative area: Uses orange color
#     image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.clump), bool_number_contours=True, color=(255, 255, 0))  # Bee clump: Uses cyan color

#     #draw more contours to visualize filtering steps


#     contours_bees.output_contours_to_images(output_path+"/contours")

#     # ------------------------------------JSON OUTPUT-------------------------------------

#     # add contour info to list
#     contour_list = []
#     for c in contours_bees.contours:
#         contour_list.append({"id": c.id,
#                                 "type": c.get_type().name,
#                                 "centroid": c.centroid,
#                                 "area": c.area,

#                                 "fitted_shape": {
#                                 "width": c.fitted_rect_width,
#                                 "height": c.fitted_rect_height,
#                                 "angle": c.fitted_rect_angle,
#                                 "area": c.fitted_ellipse_area,
#                                 "aspect_ratio": c.fitted_rect_aspect_ratio
#                                 },

#                                 "hierarchy": {
#                                 "next": int(c.hierarchy[0]) if c.hierarchy is not None else None,
#                                 "prev": int(c.hierarchy[1]) if c.hierarchy is not None else None,
#                                 "first_child": int(c.hierarchy[2]) if c.hierarchy is not None else None,
#                                 "parent": int(c.hierarchy[3]) if c.hierarchy is not None else None
#                                 },
#                                 "bee count": c.bee_count, #only for clumps
#                                 "bee count unrounded": c.bee_count_unrounded, #only for clumps
#                                 })


#     # #sort by area descending
#     # contour_list = sorted(contour_list, key=lambda x: x["area"], reverse=True)

#     #save contour list to json
#     with open(output_json_path, 'w') as f:
#         json.dump(contour_list, f, indent=4)

#     print(f"Contour data saved to {output_json_path}")

#     image_bees.save_image(output_image_path, Image.type.OUTPUT)

#     pass
