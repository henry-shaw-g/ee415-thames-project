import contour
import image
import json
import pathlib


#inputs: Image, settings file path
#outputs: Bee count, image with contours to display on frontend, 
#debug: list of contours in python memory 

def algorithm(image_path, settings_path):
    
    #Put image.png into image class instance
    settings = get_settings(settings_path)

    image = image.Image(image_path, settings)


    #do manipulations on image using class members
        #image.blur()
        #image.threshold()
        #etc

    #use thresholded image to create a contour class instance
        #new contour = contour.find_countours(image)
    pass
    

def get_settings(settings_path):
    #read settings file
    if settings_path is None:
        settings_path = "default_settings.json" 

    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    return settings



if __name__ == "__main__":
    settings_path = None
    image_path = None

    algorithm(image_path, settings_path)

    pass




