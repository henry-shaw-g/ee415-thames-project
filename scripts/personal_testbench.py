import os.path
import json
import pathlib
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

from counting.contour import Contour
from counting.contours import Contours
from counting.image import Image
from counting import algorithm

# import render_output
from utils import file_system

if __name__ == "__main__":
    input_path =  "io/input" 
    output_path = "io/output"

    # For each input image in the input directory
    # output should be put into output/{input_image_name}/ directory
    # Ignore the .hidden files like .DS_Store

    algorithm.USE_CNN_BEE_DETECTION = False

    for input_image_name in os.listdir(input_path):
        if input_image_name.startswith("."):
            continue
        input_image_path = os.path.join(input_path, input_image_name)
        output_image_path = os.path.join(output_path, input_image_name.split(".")[0], "output.jpg")
        output_json_path = os.path.join(output_path, input_image_name.split(".")[0], "output.json")

        # Create output directory if it doesn't exist
        pathlib.Path(os.path.dirname(output_image_path)).mkdir(parents=True, exist_ok=True)

        output = algorithm.algorithm(input_image_path)

        image_handle = output.image_handle
        bee_count = output.bee_count
        contours = output.contours
        print(f"Detected bee count in {input_image_name}: {bee_count}")


        image_handle.draw_contours(contours.get_contours(type = Contour.type.unprocessed), bool_number_contours=True, color=(0,255,255))  #unprocessed: Uses yellow color
        image_handle.draw_contours(contours.get_contours(type = Contour.type.rejected), color=(0,0,255))  # Rejected: Uses red color
        image_handle.draw_contours(contours.get_contours(type = Contour.type.single_bee), bool_number_contours=True, color=(0, 255,0))  # Single Bee: Uses green color
        image_handle.draw_contours(contours.get_contours(type = Contour.type.negative), bool_number_contours=True, color=(0, 128, 255))  # negative area: Uses orange color
        image_handle.draw_contours(contours.get_contours(type = Contour.type.clump), bool_number_contours=True, color=(255, 255, 0))  # Bee clump: Uses cyan color

        image_handle.save_image(output_image_path, Image.type.OUTPUT)

        contours.output_contours_to_json(output_json_path, sorted_by_area=True)

        #output text document with count info
        with open(os.path.join(output_path, input_image_name.split(".")[0], "count.txt"), 'w') as f:
            f.write(f"Detected bee count: {bee_count}\n")
            # Bee statistics
            f.write(f"Single bee area statistics: mean={contours.mean_single_bee_area}, median={contours.median_single_bee_area}, stddev={contours.stddev_single_bee_area}\n")
            f.write(f"Number of single bee contours: {len(contours.get_contours(type=Contour.type.single_bee))}\n")
            f.write(f"Number of clump contours: {len(contours.get_contours(type=Contour.type.clump))}\n")
            # clump contour count details
            f.write("Clump contour details:\n")
            for c in contours.get_contours(type=Contour.type.clump):
                f.write(f"  Contour ID: {c.id}, Area: {c.area}, Bee Count: {c.bee_count}, Bee Count Unrounded: {c.bee_count_unrounded}\n")
        

        # break  # Remove this break to process all images in the input directory