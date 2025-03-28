'''
Looking into options for highlighting shapes after color shifting
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules import img_workspace
from modules import img_helpers

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)

class EventHandler(img_workspace.WorkspaceEventHandler):
    def process(self, _):

        shifted = img.copy()
        shifted = cv.cvtColor(shifted, cv.COLOR_BGR2HSV)
        # shifted[:, :, 0] = 0
        # shifted[:, :, 1] = 255
        shifted[:, :, 2] = (shifted[:, :, 1] + shifted[:, :, 2]) / 2

        result = cv.cvtColor(shifted, cv.COLOR_HSV2BGR)
        self.workspace.push_img_bgr(result)
        path = "/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/src/cv_experiments/outputs/bee-image-1-shifted.png"
        print("savinvg image to path = {path}")
        cv.imwrite(path, result)


workspace = img_workspace.Workspace(title="Color Shifting", event_handler=EventHandler())
workspace.reg_slider_input("Threshold1", "Threshold1", 0, 1000, 100, 1)
workspace.reg_slider_input("Threshold2", "Threshold2", 0, 1000, 200, 1)
workspace.run()