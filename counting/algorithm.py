import contour
import image as image
import json
import pathlib


#inputs: Image, settings file path
#outputs: Bee count, image with contours to display on frontend, 
#debug: list of contours in python memory 

def algorithm(image_path, settings_path):
    
    settings = get_settings(settings_path)

    image_bees = image.Image(image_path, settings)
    if image_bees is None:
        raise ValueError("Image could not be loaded. Check the file path.")

    # Image processing pipeline
    image_bees.blur()
    image_bees.to_hsv()       # Convert to HSV for brightness-based thresholding
    image_bees.threshold()     # OTSU thresholding on V channel


    image_bees.show_image(image.Image_Type.CURRENT, "Thresholded Image")
    image_bees.show_image(image.Image_Type.PREVIOUS, "Thresholded Image")
    


    #use thresholded image to create a contour class instance
        #new contour = contour.find_countours(image)
    pass
    


def get_settings(settings_path):
    #read settings file
    if settings_path is None:
        settings_path = "counting/default_settings.json"

    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    return settings



if __name__ == "__main__":
    settings_path = None
    image_path =  "/Users/Connor/Pictures/Bee/bee1.jpg"

    algorithm(image_path, settings_path)



    pass




