import json
import pathlib
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

from contour import Contour
from contours import Contours
from image import Image
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

    image_bees = Image(image_path, settings)
    if image_bees is None:
        raise ValueError("Image could not be loaded. Check camera or file path.")

    # Image processing pipeline
    #Possible steps: resize, exposure normalization. Might not be neccessary for static camera and enclosure
    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.extract_v() #extract just the V channel
    image_bees.expose_piecewise_std() # Expose the V channel
    image_bees.threshold()    # OTSU thresholding on V channel
    image_bees.morphology()  # maybe not needed, I couldnt see many small holes and they will be taken out in the filter area pass
    #image_bees.morphology()  # maybe not needed, I couldnt see many small holes

    contours_bees = Contours(image_bees.get_image(Image.type.CURRENT), image_bees.get_image(Image.type.ORIGINAL), settings)

    contours_bees.find_contours()

    # basic size filtering to git rid of small noise contours
    contours_bees.filter_contours_area()

    # 

    # Contour processing pipeline
    contour_bees = Contour(image_bees.get_image(Image.type.CURRENT), settings)


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
    output_hierarchy_path = output_path + "/hierarchy.txt"

    # algorithm(image_path, settings_path)

    settings = get_settings(settings_path)

    image_bees = Image(input_image_path, settings)

    # print image dimensions for debug purposes
    img_height, img_width = image_bees.current_image.shape[:2]
    img_area = img_height * img_width
    print(f"Image dimensions: {img_width}x{img_height}, area: {img_area}")


    # #create plot with 4 graphs in 2x2 grid
    # #first plot will be brightness histogram
    # plt.hist(image_bees.get_image(Image.type.CURRENT).ravel(),256,[0,256]); 
    # plt.title('Brightness Histogram for input image')
    # plt.show()

    # Image processing pipeline
    #Possible steps: resize, exposure normalization. Might not be neccessary for static camera and enclosure

    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.extract_v() #extract just the V channel
    image_bees.expose_piecewise_std() # Expose the V channel
    image_bees.threshold()    # OTSU thresholding on V channel
    image_bees.morphology()  # maybe not needed, I couldnt see many small holes and they will be taken out in the filter area pass

    # image_bees.show_image(Image.type.CURRENT, "Thresholded Image")

    contours_bees = Contours(image_bees.get_image(Image.type.CURRENT), image_bees.get_image(Image.type.ORIGINAL), settings)

    contours_bees.find_contours()

    # basic size filtering to git rid of small noise and large contours TODO: ramp back a little bit
    contours_bees.filter_contours_area()

    # TODO: Filter using hierarchy, if its small and not inside another contour, reject it

    # TODO: filter singles vs clumps using fitted ellipse aspect ratio and comparing contour area to ellipse area
    # contours_bees.filter_contours_aspect_ratio()

    # TODO: filter negative vs rejected contours by color, and increase area of negative contours using watershed
    # contours_bees.filter_contours_color()
    # contours_bees.increase_negative_contour_area()



    # TODO: calculate clump count using area based on average single bee area

    # TODO: generate count

    image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.unprocessed), bool_number_contours=True)  #unprocessed: Uses default green color
    image_bees.draw_contours(contours_bees.get_contours(type = Contour.type.rejected), color=(0,0,255))  # Rejected: Uses red color

    #draw more contours to visualize filtering steps

    # END TODO


    
    contours_bees.output_contours_to_images(output_path+"/contours")

    # add contour info to list
    contour_list = []
    for c in contours_bees.contours:
        # print(f"Contour {i}: Area={c.area}, Aspect Ratio={c.fitted_ellipse_aspect_ratio}")
        contour_list.append({"id": c.id,
                             "type": c.get_type().name,
                             "centroid": c.centroid,
                             "area": c.area,
                             # if aspect ratio is NaN set to -1
                             "aspect_ratio": c.fitted_ellipse_aspect_ratio if not np.isnan(c.fitted_ellipse_aspect_ratio) else -1,
                             "hierarchy_Next_Prev_FirstChild_Parent": {
                                "next": int(c.hierarchy[0]) if c.hierarchy is not None else None,
                                "prev": int(c.hierarchy[1]) if c.hierarchy is not None else None,
                                "first_child": int(c.hierarchy[2]) if c.hierarchy is not None else None,
                                "parent": int(c.hierarchy[3]) if c.hierarchy is not None else None
                             }

                             #average HSV values from original image

                             })


    #sort by area descending
    contour_list = sorted(contour_list, key=lambda x: x["area"], reverse=True)

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