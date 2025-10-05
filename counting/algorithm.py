import json
import pathlib
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

import contour
import contours
import image 
import render_output
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

    image_bees = image.Image(image_path, settings)
    if image_bees is None:
        raise ValueError("Image could not be loaded. Check camera or file path.")

    # Image processing pipeline
    #Possible steps: resize, exposure normalization. Might not be neccessary for static camera and enclosure
    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.threshold()    # OTSU thresholding on V channel
    #image_bees.morphology()  # maybe not needed, I couldnt see many small holes

    # Contour processing pipeline
    contour_bees = contour.Coutour(image_bees.get_image(image.Image_Type.CURRENT), settings)


    pass
    

'''
class: AlgorithmOutput
    Pretty much just to specify and hold all outputs of algorithm.
'''
class AlgorithmOutput():
    def __init__(self):
        self.bee_count = 0
        self.output_image = None    # bgr3 array
        self.contours = []          # list of contours found in the image, needs to identify clumps

    '''
    fn: set
    inputs: dict with keys "bee_count", "output_image", "contours"
    '''
    def set(self, dict):
        self.bee_count = dict.get("bee_count", 0)
        self.output_image = dict.get("output_image", None)
        self.contours = dict.get("contours", [])
    
'''
function: get_settings
inputs: settings file path
outputs: settings dict
'''
def get_settings(settings_path):
    #read settings file
    if settings_path is None:
        settings_path = "counting/default_settings.json"

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

    # algorithm(image_path, settings_path)

    settings = get_settings(settings_path)

    image_bees = image.Image(input_image_path, settings)
    if image_bees is None:
        raise ValueError("Image could not be loaded. Check camera or file path.")

    # print image dimensions for debug purposes
    img_height, img_width = image_bees.current_image.shape[:2]
    img_area = img_height * img_width
    print(f"Image dimensions: {img_width}x{img_height}, area: {img_area}")


    #create plot with 4 graphs in 2x2 grid
    #first plot will be brightness histogram
    plt.hist(image_bees.get_image(image.Image_Type.CURRENT).ravel(),256,[0,256]); 
    plt.title('Brightness Histogram for input image')

    # Image processing pipeline
    #Possible steps: resize, exposure normalization. Might not be neccessary for static camera and enclosure

    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.extract_v() #extract just the V channel
    image_bees.expose_piecewise_std() # Expose the V channel
    image_bees.threshold()    # OTSU thresholding on V channel
    image_bees.morphology()  # maybe not needed, I couldnt see many small holes and they will be taken out in the filter area pass

    # image_bees.show_image(image.Image_Type.CURRENT, "Thresholded Image")

    contours_bees = contours.Contours(image_bees.get_image(image.Image_Type.CURRENT), image_bees.get_image(image.Image_Type.ORIGINAL), settings)

    contours_bees.find_contours()

    # basic size filtering to git rid of small noise contours
    contours_bees.filter_contours_area()

    # 


    print(f"Found {len(contours_bees.contours)} contours")

    image_bees.draw_numbered_contours([c.contour for c in contours_bees.contours])  # Uses default green color

    contours_bees.output_contours_to_image(output_path)


    # add contour info to list
    contour_list = []
    for i, c in enumerate(contours_bees.contours):
        # print(f"Contour {i}: Area={c.area}, Aspect Ratio={c.fitted_ellipse_aspect_ratio}")
        contour_list.append({"index": i,
                             "centroid": c.centroid,
                             "area": c.area,
                             "aspect_ratio": c.fitted_ellipse_aspect_ratio})

    #sort by area descending
    contour_list = sorted(contour_list, key=lambda x: x["area"], reverse=True)

    #save contour list to json
    with open(output_json_path, 'w') as f:
        json.dump(contour_list, f, indent=4)
    
    print(f"Contour data saved to {output_json_path}")

    image_bees.save_image(output_image_path, image.Image_Type.CURRENT)

    plt.show()

    pass




