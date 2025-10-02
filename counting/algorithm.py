import json
import pathlib

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
    dir_path =  "/Users/clous/Documents/Bee"
    image_path = dir_path + "/bee1.jpg"
    output_path = dir_path + "/output.jpg"

    # image_path =  "/Users/Connor/Pictures/Bee/bee1.jpg"

    # algorithm(image_path, settings_path)

    settings = get_settings(settings_path)

    image_bees = image.Image(image_path, settings)
    if image_bees is None:
        raise ValueError("Image could not be loaded. Check camera or file path.")

    # Image processing pipeline
    #Possible steps: resize, exposure normalization. Might not be neccessary for static camera and enclosure

    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.threshold()    # OTSU thresholding on V channel
    image_bees.morphology()  # maybe not needed, I couldnt see many small holes

    # image_bees.show_image(image.Image_Type.CURRENT, "Thresholded Image")

    contours_bees = contours.Contours(image_bees.get_image(image.Image_Type.CURRENT), settings)

    contours_bees.find_contours()

    print(f"Found {len(contours_bees.contours)} contours")

    image_bees.draw_numbered_contours([c.contour for c in contours_bees.contours])  # Uses default green color

    #print areas of contours
    for i, c in enumerate(contours_bees.contours):
        print(f"Contour {i}: Area={c.area}, Aspect Ratio={c.fitted_ellipse_aspect_ratio}")


    image_bees.save_image(output_path, image.Image_Type.CURRENT)

    pass




