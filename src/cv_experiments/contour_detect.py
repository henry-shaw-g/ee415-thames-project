'''
Currently a script, do not use an imported module.
'''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules import img_workspace

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)
img = img[:, 500:3000, :]

def saturate(img_bgr, k):
    img_hsv = cv.cvtColor(img_bgr, cv.COLOR_BGR2HSV)
    img_hsv[:, :, 1] = np.clip(k * img_hsv[:, :, 1], 0, 255)
    return cv.cvtColor(img_hsv, cv.COLOR_HSV2BGR)

class EventHandler(img_workspace.WorkspaceEventHandler):
    def process(self, _):
        workspace = self.workspace
        filter_size = (workspace.check_slider_input("FSIZE") * 2) - 1
        filter_sigma = workspace.check_slider_input("FSIGMA") / 100
        # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        saturated = saturate(img, 3)
        gray = cv.cvtColor(saturated, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(saturated, (filter_size, filter_size), filter_sigma)
        # _, gray = cv.threshold(gray, t, 255, cv.THRESH_BINARY_INV)
        workspace.push_img_bgr(blurred)

        edge_thresh1 = workspace.check_slider_input("ET1")
        edge_thresh2 = workspace.check_slider_input("ET2")

        edges = cv.Canny(blurred, edge_thresh1, edge_thresh2)
        contours, _ = cv.findContours(edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        hulls = []
        ellipses = []
        for contour in contours:
            hull = cv.convexHull(contour)
            if len(hull) > 4:
                ellipse = cv.fitEllipse(hull)
                aspect_ratio = ellipse[1][0] / ellipse[1][1]
                print(aspect_ratio)
                if 0.1 < aspect_ratio < 0.7:
                    ellipses.append(ellipse)
            # check aspect ratio of hull
            hulls.append(hull)

        # masked = cv.bitwise_and(img, img, mask=gray)
        print(f"#countors: {len(contours)}")
        marked = blurred #cv.cvtColor(gray.copy(), cv.COLOR_GRAY2BGR)
        marked = cv.drawContours(marked, contours, -1, (128, 200, 128), thickness=1, lineType=cv.LINE_8)
        marked = cv.drawContours(marked, hulls, -1, (0, 0, 255), thickness=4, lineType=cv.LINE_8)
        for ellipse in ellipses:
            cv.ellipse(marked, ellipse, (255, 0, 0), thickness=2)

        workspace.push_img_bgr(marked)
    
workspace = img_workspace.Workspace(title="Contour Detection", event_handler=EventHandler())
workspace.reg_slider_input("FSIZE", "filter-size", 1, 6, 1, 1) # todo: figure out how to constrain to odd
workspace.reg_slider_input("FSIGMA", "filter-sigma", 0, 300, 100, 2)
workspace.reg_slider_input("ET1", "edge-thresh-1", 0, 200, 100, 3)
workspace.reg_slider_input("ET2", "edge-thresh-2", 0, 400, 200, 4)

workspace.run()
