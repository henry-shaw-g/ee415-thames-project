'''
Detect discrete shapes off of the background. Uses a binary thresholding and then contour detection.
Next possible step will be to apply multiple stages with different thresholds and smoothings to see if individual bees in clumps
can be detected after detecting clumps originally. If this is not possible, then use multiple stages to get more accurate pixel counts
in clumps.
'''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules import img_workspace
from modules import img_helpers

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)

# Hand picked params for single bee identification. Some of these are
# used as defaults in gui widgets.
# In the future this will need to be checked against general bee sizes (ask Dr. Hopkins).
# Also, will need markers to give space / scale sense, possible also rotation / translation adjustments for pixel counting ...

FILTER_SIZE_1 = 5
FILTER_SIGMA_1 = 250

FILTER_SIZE_2 = 1       # forgot if 1 was no filter or 1x1 kernel
FILTER_SIGMA_2 = 20

BEE_WIDTH_MIN = 40
BEE_WIDTH_MAX = 70
BEE_HEIGHT_MIN = 90
BEE_HEIGHT_MAX = 120
BEE_AR_MIN = 1.5
BEE_AR_MAX = 3

def saturate(img_bgr, k):
    img_hsv = cv.cvtColor(img_bgr, cv.COLOR_BGR2HSV)
    img_hsv[:, :, 1] = np.clip(k * img_hsv[:, :, 1], 0, 255)
    return cv.cvtColor(img_hsv, cv.COLOR_HSV2BGR)

def get_otsu_thresh(gray):
    # yanked directly from Open CV tutorials
    hist = cv.calcHist([gray],[0],None,[256],[0,256])
    hist_norm = hist.ravel()/hist.sum()
    Q = hist_norm.cumsum()
    
    bins = np.arange(256)
    
    fn_min = np.inf
    thresh = -1
    
    for i in range(1,256):
        p1,p2 = np.hsplit(hist_norm,[i]) # probabilities
        q1,q2 = Q[i],Q[255]-Q[i] # cum sum of classes
        if q1 < 1.e-6 or q2 < 1.e-6:
            continue
        b1,b2 = np.hsplit(bins,[i]) # weights
    
        # finding means and variances
        m1,m2 = np.sum(p1*b1)/q1, np.sum(p2*b2)/q2
        v1,v2 = np.sum(((b1-m1)**2)*p1)/q1,np.sum(((b2-m2)**2)*p2)/q2
    
        # calculates the minimization function
        fn = v1*q1 + v2*q2
        if fn < fn_min:
            fn_min = fn
            thresh = i
    return thresh

def binarize_pass(gray, fsize, fsigma):
    blurred = cv.GaussianBlur(gray, (fsize, fsize), fsigma)
    ret, binarized = cv.threshold(blurred, get_otsu_thresh(blurred), 255, cv.THRESH_BINARY)
    return binarized

class EventHandler(img_workspace.WorkspaceEventHandler):
    def process(self, _):
        print("Processing image ...")

        workspace = self.workspace
        
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        filter_size_1 = (workspace.check_slider_input("FSIZE1") * 2) - 1
        filter_sigma_1 = workspace.check_slider_input("FSIGMA1") / 100
        gray = binarize_pass(gray, filter_size_1, filter_sigma_1)
        
        filter_size_2 = (workspace.check_slider_input("FSIZE2") * 2) - 1
        filter_sigma_2 = workspace.check_slider_input("FSIGMA2") / 100
        gray = binarize_pass(gray, filter_size_2, filter_sigma_2)

        # blurred = cv.GaussianBlur(gray, (filter_size_1, filter_size_1), filter_sigma_1)
        # _, gray = cv.threshold(gray, t, 255, cv.THRESH_BINARY_INV)
        # workspace.push_img_bgr(blurred)
        # binary_thresh = workspace.check_slider_input("BT")
        # binary_thresh = get_otsu_thresh(blurred)
        # ret, binarized = cv.threshold(gray, binary_thresh, 255, cv.THRESH_BINARY)
        # filter_size_2 = (workspace.check_slider_input("FSIZE2") * 2) - 1
        # filter_sigma_2 = workspace.check_slider_input("FSIGMA2") / 100
        # blurred = cv.GaussianBlur(binarized, (filter_size_2, filter_size_2), filter_sigma_2)

        # edge_thresh1 = workspace.check_slider_input("ET1")
        # edge_thresh2 = workspace.check_slider_input("ET2")

        # edges = cv.Canny(blurred, edge_thresh1, edge_thresh2)
        
        
        contours, _ = cv.findContours(gray, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
        hulls = []
        ellipses = []
        ellipses_result = []
        ellipse_ars = []

        bee_width_min, bee_width_max = workspace.check_range_input("BEE_WIDTH")
        bee_height_min, bee_height_max = workspace.check_range_input("BEE_HEIGHT")
        bee_ar_min, bee_ar_max = workspace.check_range_input("BEE_AR")

        print(f"{bee_width_min=}, {bee_width_max=}")
        print(f"{bee_height_min=}, {bee_height_max=}")
        print(f"{bee_ar_min=}, {bee_ar_max=}")

        for contour in contours:
            hull = cv.convexHull(contour)
            if len(hull) > 4:
                ellipse = cv.fitEllipse(contour)
                aspect_ratio = ellipse[1][1] / ellipse[1][0]
                ellipses.append(ellipse)
                ellipse_ars.append(aspect_ratio)
                #print(aspect_ratio)
                width_good = bee_width_min < ellipse[1][0] < bee_width_max
                height_good = bee_height_min < ellipse[1][1] < bee_height_max
                ar_good = bee_ar_min < aspect_ratio < bee_ar_max
                if width_good and height_good and ar_good:
                    ellipses_result.append(True)
                else:
                    ellipses_result.append(False)
                    
            # check aspect ratio of hull
            hulls.append(hull)

        # masked = cv.bitwise_and(img, img, mask=gray)
        # print(f"#countors: {len(contours)}")
        marked = cv.cvtColor(gray.copy(), cv.COLOR_GRAY2BGR)
        marked = cv.drawContours(marked, contours, -1, (0,255,0), 3)
        marked = cv.drawContours(marked, hulls, -1, (0, 0, 255), thickness=4, lineType=cv.LINE_8)

        # do the zipper iterate thing
        for i, ellipse in enumerate(ellipses):
            if ellipses_result[i]:
                cv.ellipse(marked, ellipse, (255, 0, 0), thickness=2)
                img_helpers.ez_draw_text(marked, f"{ellipse_ars[i]}", (int(ellipse[0][0]), int(ellipse[0][1])), (255, 255, 255))
            else:
                pass
                # cv.ellipse(marked, ellipse, (255, 0, 255), thickness=2)
            

        workspace.push_img_bgr(marked)
    
workspace = img_workspace.Workspace(title="Contour Detection", event_handler=EventHandler())
workspace.reg_slider_input("FSIZE1", "filter-size-1", 1, 6, 6) # todo: figure out how to constrain to odd
workspace.reg_slider_input("FSIGMA1", "filter-sigma-1", 0, 300, 100)
workspace.reg_slider_input("FSIZE2", "filter-size-2", 1, 6, 1) # todo: figure out how to constrain to odd
workspace.reg_slider_input("FSIGMA2", "filter-sigma-2", 0, 300, 20)

workspace.reg_range_input("BEE_WIDTH", "bee-width-range", (0, 200), (BEE_WIDTH_MIN, BEE_WIDTH_MAX))
workspace.reg_range_input("BEE_HEIGHT", "bee-height-range", (0, 200), (BEE_HEIGHT_MIN, BEE_HEIGHT_MAX))
workspace.reg_range_input("BEE_AR", "bee-aspectratio-range", (0, 5), (BEE_AR_MIN, BEE_AR_MAX))

# workspace.reg_slider_input("ET1", "edge-thresh-1", 0, 200, 100, 4)
# workspace.reg_slider_input("ET2", "edge-thresh-2", 0, 400, 200, 5)

workspace.run()