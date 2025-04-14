'''
Algorithm for counting bees (based on area), filtering contours, and ordering them.
'''
import cv2 as cv
import numpy as np
import os
import json

RUN_TESTS = True

# offline gamma correction lookup table
# https://pyimagesearch.com/2015/10/05/opencv-gamma-correction/
gamma_correction = 0.5
gamma_offset = -0.1
gamma_LUT = np.arange(256, dtype=np.float32) / 255.0
gamma_LUT = np.clip(np.power(gamma_LUT + gamma_offset, gamma_correction), 0, 1) * 255.0
gamma_LUT = np.uint8(gamma_LUT)

'''
function:
    Gets a good threshold for binarization.
'''
def _get_otsu_thresh(gray):
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

'''
INPUT:  img: Any RGB image
OUTPUT: Image with preprocessed effects applied
'''
def image_preprocessing(img, img_scale = 0.5, img_exposure=1.5):
    #resize
    img_preprocessed = cv.resize(img, None, fx=img_scale, fy=img_scale, interpolation=cv.INTER_CUBIC)
    #exposure
    # img_preprocessed = cv.convertScaleAbs(img_preprocessed,alpha=img_exposure,beta=0)
    img_preprocessed = cv.LUT(img_preprocessed, gamma_LUT)
    #blur
    img_preprocessed = cv.GaussianBlur(img_preprocessed, (5, 5), 3)

    return img_preprocessed

''' 
input:  img:    HSV image
        lowerV: lower value 
function: 
    Creates an image threshold based on the brightness value determined in lowerV
    Excludes any brightness between lowerV and 255
return: a threshold image
'''
def image_threshold(img, lowerV=0):
    lower=(0,0,lowerV)
    upper=(255,255,255)
    thresh = cv.inRange(img,lower,upper)
    
    # we could potentially in the future get two masks and cv.bitwise_or or cv.bitwise_and them
    # https://stackoverflow.com/questions/48109650/how-to-detect-two-different-colors-using-cv2-inrange-in-python-opencv
    return thresh

'''
input:  contour_idx: index of the contour to check
        heirarchy: the heirarchy of the contours
function:
    Check if the contour is an external contour, i.e not a hole within another contour, ignoring the top level contour which is the image itself.
return: bool
'''
def _contour_check_external(contour_idx, heirarchy):
    # note: this may break if the screen bounding contour doesn't show up for some reason
    return heirarchy[0][contour_idx][3] == 0

'''
input:  contours: list (with proper indexing) of contours
        contour_idx: index of the contour to check
        heirarchy: the heirarchy of the contours
function:
        Get the area of the contour, excluding the area of immediate child contours (significant holes).
'''
def _contour_get_area_no_holes(contours, contour_idx, heirarchy):
    area = cv.contourArea(contours[contour_idx])

    child_idx = heirarchy[0][contour_idx][2] # get first child of the contour
    while child_idx != -1: # only check first sub level of contours (dont care about anything finer than that)
        area -= cv.contourArea(contours[child_idx])
        child_idx = heirarchy[0][child_idx][0] # get next child in this level
    
    return area

def contour_findContours(imgThresh):
    contours, hierarchy = cv.findContours(imgThresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # in the future put these into a class or some other type of data structure.

    return contours, hierarchy #In the future return one object


def contour_filterContours(contours):
    pass


class CountingSettings:
    def __init__(self):
        self.img_scale = 0.5
        self.img_exposure = 1.5
        self.lowerV = 0
        self.filter_size_1 = 5
        self.filter_sigma_1 = 3
        self.filter_size_2 = 5
        self.filter_sigma_2 = 3

def _read_image_metadata(imgpath, metadatapath):
    # check if image is in the same directory as the data file
    if os.path.dirname(imgpath) == os.path.dirname(metadatapath):
        key = os.path.basename(imgpath)
        with open(metadatapath, 'r') as f:
            data = json.load(f)
            if key in data:
                return data[key]
            else:
                raise RuntimeError(f"Image {key} not found in metadata file.")
    else:
        raise RuntimeError("Image and metadata file are not in the same directory.")

def _read_settings():
    def __init__(self):
        self.annotated_img = None
        self.count = 666
        self.average_single_bee_area = 420
        self.single_bee_num = 90

class CountingResult:
    def __init__():
        pass

'''
class:  Counting worker class.
todo:   restructure this to be more memory friendly when we do live video feed.
'''
class Counting:
    DETECT_NONE = 0
    DETECT_SINGLE = 1
    DETECT_CLUMP = 2

    def __init__(self, img, predefined_roi=None, use_marker_roi=True, metadata_paths=None):
        self.w_range = (0, 0)   # ellipse width range for single bee
        self.h_range = (0, 0)   # ellipse height range for single bee
        self.ar_range = (0, 0)  # ellipse aspect ratio range for single bee

        # image specific algorithm tuning parameters. Use for TESTING ONLY!
        # This will overwrite predefined_roi parameter.
        if metadata_paths:
            meta_imgpath = metadata_paths[0]
            meta_datapath = metadata_paths[1]
            data = _read_image_metadata(meta_imgpath, meta_datapath)
            self.w_range = (data["w_range"][0], data["w_range"][1])
            self.h_range = (data["h_range"][0], data["h_range"][1])
            self.ar_range = (data["ar_range"][0], data["ar_range"][1])
            if "roi" in data:
                predefined_roi = data["roi"]

        # apply region of interest if specified
        if predefined_roi:
            img = img[predefined_roi[0][0]:predefined_roi[0][1], predefined_roi[0]:predefined_roi[1][0]:predefined_roi[1][1]]

        self.img_bgr = img
        self.img_bin = None
        self.img_draw = None
        
        # map contours to hull and ellipse indicies
        self.contours = None
        self.heirarchy = None
        # self.hulls = []
        self.computed = None # [ellipse, is_external, detect_state]
        
        # output vars
        self.n_total = 0
        self.n_single = 0

    def count() -> CountingResult:
        return CountingResult()

    def _preprocess(self):
        self.img_bgr = image_preprocessing(self.img_bgr)
        img_hsv = cv.cvtColor(self.img_bgr, cv.COLOR_BGR2HSV)
        th = _get_otsu_thresh(img_hsv[:, :, 2])
        self.img_bin = image_threshold(img_hsv, th)

    def _get_shapes(self):
        contours, heirarchy = contour_findContours(self.img_bin)
        self.contours = contours
        self.heirarchy = heirarchy
        self.computed = [None] * len(contours)

        for i, contour in enumerate(contours):
            hull = cv.convexHull(contour)
            if len(hull) > 4:
                ellipse = cv.fitEllipse(hull)
                is_external = _contour_check_external(i, heirarchy)
                self.computed[i] = [ellipse, is_external, Counting.DETECT_NONE]
            else:
                self.computed[i] = [None, False, Counting.DETECT_NONE]
                
    '''
    precondition:
            have already called _get_shapes()
    '''
    def _filter_single_bees(self):
        for (i, c_data) in enumerate(self.computed):
            if c_data[0] is None or not c_data[1]: continue
            # only consider external contours

            ellipse = c_data[0]
            w = ellipse[1][0]
            h = ellipse[1][1]
            ar = h / w
            print(f"single-bee check: {w=}, {h=}, {ar=}")

            if \
            self.w_range[0] <= w <= self.w_range[1] and \
            self.h_range[0] <= h <= self.h_range[1] and \
            self.ar_range[0] <= ar <= self.ar_range[1]:
                self.computed[i][2] = Counting.DETECT_SINGLE

    '''
    precondition:
            have already called _filter_single_bees()
    '''
    def _filter_clumps(self):
        for i, status, contour in zip(range(len(self.computed)), self.computed, self.contours):
            # only consider external contours
            if status[0] is not None and status[1] and status[2] != Counting.DETECT_SINGLE:
                bbox = cv.boundingRect(contour)
                *_, w, h = bbox
                if w > self.w_range[0] and h > self.h_range[0]:
                    status[2] = Counting.DETECT_CLUMP

    def _get_count(self):
        single_bee_n = 0
        single_bee_area_sum = 0
        clump_area_sum = 0

        for i, c_data, contour in zip(range(len(self.computed)), self.computed, self.contours):
            if c_data[2] == Counting.DETECT_SINGLE:
                single_bee_n += 1
                single_bee_area_sum += cv.contourArea(contour)
            elif c_data[2] == Counting.DETECT_CLUMP:
                clump_area_sum += _contour_get_area_no_holes(self.contours, i, self.heirarchy)

        bee_area_avg = single_bee_area_sum / single_bee_n if single_bee_n > 0 else 0
        bee_n = single_bee_n + clump_area_sum / bee_area_avg if bee_area_avg > 0 else 0

        self.n_total = bee_n
        self.n_single = single_bee_n
        return bee_n

    def _draw_init(self):
        self.img_draw = self.img_bgr.copy()

    def _draw_contours(self):
        cv.drawContours(self.img_draw, self.contours, -1, (0, 255, 0), 2)

    def _draw_single_bees(self):
        for i, c_data in enumerate(self.computed):
            if c_data[2] == Counting.DETECT_SINGLE:
                ellipse = c_data[0]
                cv.ellipse(self.img_draw, ellipse, (255, 0, 255), 4)

    def _draw_clumps(self):
        for i, status, contour in zip(range(len(self.computed)), self.computed, self.contours):
            if status[2] == Counting.DETECT_CLUMP:
                bbox = cv.boundingRect(contour)
                cv.rectangle(self.img_draw, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 0), 2)

    def _draw_ellipses(self):
        pass

## TESTING ##
if __name__ == "__main__" and RUN_TESTS:
    img = cv.imread("images/bee-image-samples/bee-image-1.jpg")
    if img is None:
        raise RuntimeError("Image file cannot be read.")
    

    counting = Counting(img)
    counting.w_range = (15, 60)
    counting.h_range = (30, 110)
    counting.ar_range = (1, 3.0)

    counting._preprocess()
    cv.imwrite('temp/preprocessed.jpg', counting.img_bgr)
    cv.imshow("out", counting.img_bgr)
    cv.waitKey(0)
    

    counting._get_shapes()
    counting._filter_single_bees()
    counting._filter_clumps()
    bee_n = counting._get_count()
    print(f"Total bees: {bee_n}")

    counting._draw_init()
    counting._draw_contours()
    counting._draw_single_bees()
    counting._draw_clumps()
    cv.imshow("out", counting.img_draw)
    cv.waitKey(0)

    


    cv.destroyAllWindows()