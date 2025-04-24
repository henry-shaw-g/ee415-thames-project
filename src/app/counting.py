'''
Algorithm for counting bees (based on area), filtering contours, and ordering them.
'''
import sys
import cv2 as cv
import numpy as np
import os
import json

# for single script testing
if __name__ == "__main__":
    import sys
    if not ('src' in sys.path):
        sys.path.append('src')


from util import color_mod, color_depth, masking

RUN_TESTS = True

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
function:
    Appropriately resize the image to roughly 1920x1080
'''
def _get_auto_resize_factor(img):
    dim = img.shape
    dim_min = min(dim[0], dim[1])
    return 1080 / dim_min



'''
INPUT:  img: Any RGB image
OUTPUT: Image with preprocessed effects applied
'''
def image_preprocessing(img, img_scale = None):
    if img_scale is None:
        img_scale = _get_auto_resize_factor(img)
    #resize
    img_preprocessed = cv.resize(img, None, fx=img_scale, fy=img_scale, interpolation=cv.INTER_CUBIC)
    #exposure
    # img_preprocessed = cv.convertScaleAbs(img_preprocessed,alpha=img_exposure,beta=0)
    img_preprocessed = color_mod.expose_piecewise_std(img_preprocessed)
    #blur
    img_preprocessed = cv.GaussianBlur(img_preprocessed, (5, 5), 0)

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
    return heirarchy[0][contour_idx][3] == -1

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

'''
class:
    Manages reading / writing / requesting settings. Allows us to manipulate config while the program is running.
'''
class CountingSettings:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.dict = {}

        # TODO: activation here

    '''
    function:
        Refreshes settings from the json file. Also writes any settings provided by the algorithm.
        Call this everytime the algorithm runs or something.
    '''
    def refresh(self):
        # get settings from file
        try:
            f = open(self.json_file_path, 'r')
        except:
            read = {}
        else:
            with f:
                read = json.load(f)
        
        # check if settings from file are missing any required settings from last run 
        diff = set(self.dict.keys()) - set(read.keys())
        # merge, preferring read settings
        self.dict = self.dict | read    
        if len(diff) <= 0:
            return
        
        with open(self.json_file_path, 'w') as f:
            json.dump(self.dict, f, indent='\t')

    '''
    function:
        Get a setting or a provided default.
    input:  key: string identifier of the setting requested.
            default: backup value provided by the algorithm code. This also gets put into the json file.
    TODO: have some kind of mechanism to handle type conflicts.
    '''
    def get(self, key,  default):
        if key in self.dict:
            return self.dict[key]
        else:
            self.dict[key] = default
            return default
        
    '''
    function:
        Just prints the settings.
    '''
    def print(self):
        print(json.dumps(self.dict, indent='\t'))

'''
function:
    Was used when there was specific configs per image. Probably should go unused.
'''
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

class CountingResult:
    def __init__():
        pass

class Contour:
    def __init__(self, pts, ellipse):
        self.pts = pts
        self.ellipse = ellipse

'''
class:  Counting worker class.
todo:   restructure this to be more memory friendly when we do live video feed.
'''
class Counting:
    DETECT_NONE = 0
    DETECT_SINGLE = 1
    DETECT_CLUMP = 2

    def __init__(self, img, settings: CountingSettings, predefined_roi=None, use_marker_roi=True, metadata_paths=False):
        # load settings
        self.settings = settings

        self.w_range = settings.get('w_range', (50, 100))       # ellipse width range for single bee
        self.h_range = settings.get('h_range', (50, 200))       # ellipse height range for single bee
        self.w_max = settings.get('w_max', 300)                 # reject ellipse size for bee size guess stage
        self.h_max = settings.get('h_max', 300)                 # '''
        self.filter_abs_size = settings.get('filter_abs_size', False)

        self.filter_rel_size_stdl = settings.get('rel_size_stdl', (1, 1))        # single bee size std. deviations low reject
        self.filter_rel_size_stdh = settings.get('rel_size_stdh', (1, 1))     # single bee size std. deviatoins high reject
        self.filter_rel_size_perl = settings.get('rel_size_perl', (0.3, 0.5))
        self.filter_rel_size_perh = settings.get('rel_size_perh', (0.3, 0.5))
        self.filter_rel_mode = settings.get('rel_size_mode', "per")

        self.filter_ellipse_area_fit = True
        self.ellipse_area_fit_thresh = settings.get('ellipse_area_fit_thresh', 0.3)

        self.ar_range = settings.get('ar_range', (1.5, 3.5))  # single bee aspect ration filter

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
        if predefined_roi is not None:
            img = img[predefined_roi[0][0]:predefined_roi[0][1], predefined_roi[0]:predefined_roi[1][0]:predefined_roi[1][1]]

        if use_marker_roi:
            pass

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

    def count(self) -> CountingResult:
        # reset state

        # display settings
        self.settings.print()

        # preprocess image
        self._preprocess()

        # get shapes
        self._get_shapes()

        # filter single bees
        if self.filter_abs_size:
            self._filter_single_bees_abs()
        else:
            self._filter_single_bees_rel()

        # filter clumps
        self._filter_clumps()

        # get count
        bee_n = self._get_count()

        # draw results
        self._draw_init()
        self._draw_contours()
        self._draw_single_bees()
        self._draw_clumps()
        
        return bee_n


    def draw_results_all(self):
        self._draw_init()
        self._draw_contours()
        self._draw_single_bees()
        self._draw_clumps()
        self._draw_rejected()

    def _preprocess(self):
        self.img_bgr = image_preprocessing(self.img_bgr)
        img_hsv = cv.cvtColor(self.img_bgr, cv.COLOR_BGR2HSV)
        th = _get_otsu_thresh(img_hsv[:, :, 2])
        self.img_bin = ~image_threshold(img_hsv, th)
        # self.img_bin = cv.morphologyEx(self.img_bin, cv.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=2)

    def _get_shapes(self):
        contours, heirarchy = contour_findContours(self.img_bin)
        self.contours = contours
        self.heirarchy = heirarchy # not sure why but the first axis of heirachy just exists, is always 1 dim
        self.computed = [None] * len(contours)
        
        self.ct_areas = [0] * len(contours)

        for i, contour in enumerate(contours):
            hull = cv.convexHull(contour)
            if len(hull) > 4:
                ellipse = cv.fitEllipse(hull)
                is_external = _contour_check_external(i, heirarchy)
                print(f"i= {i},parent={heirarchy[0][i][3]}")
                self.computed[i] = [ellipse, is_external, Counting.DETECT_NONE, 0]

                area = cv.contourArea(contour)
                self.ct_areas[i] = area
            else:
                self.computed[i] = [None, False, Counting.DETECT_NONE, 0]
                
    '''
    precondition:
            have already called _get_shapes()
    '''
    def _filter_single_bees_abs(self):
        print("filtering single bees abs")

        arr = []

        for (i, c_data) in enumerate(self.computed):
            print(c_data[0], c_data[1])
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
            have already called _get_shapes()
    '''
    def _filter_single_bees_rel(self):

        arr = []

        for (i, c_data) in enumerate(self.computed):
            if c_data[0] is None or not c_data[1]: continue

            ellipse = c_data[0]
            w = ellipse[1][0]
            h = ellipse[1][1]
            ar = h / w
            
            # check how reasonable of an ellipse by area comparison
            area_ellipse = np.pi * w * h / 4
            area_ct = self.ct_areas[i]
            fit = np.abs(area_ct / area_ellipse - 1)

            print(f"single-bee check 1: {w=}, {h=}, {ar=}, {fit=}")

            if self.ar_range[0] <= ar <= self.ar_range[1] \
            and w < self.w_max and h < self.h_max and fit < self.ellipse_area_fit_thresh:
                arr.append([i, w, h])

        arr = np.array(arr)
        w_med = np.median(arr[:, 1], axis=0)
        w_std = np.std(arr[:, 1], axis=0)
        h_med = np.median(arr[:, 2], axis=0)
        h_std = np.std(arr[:,2], axis=0)


        if self.filter_rel_mode == "per":
            w_range = (w_med - w_med * self.filter_rel_size_perl[0], w_med + w_med * self.filter_rel_size_perh[0])
            h_range = (h_med - h_med * self.filter_rel_size_perl[1], h_med + h_med * self.filter_rel_size_perh[1])
        elif self.filter_rel_mode == "std":
            w_range = (w_med - w_std * self.filter_rel_size_stdl[0], w_med + w_std * self.filter_rel_size_stdh[0])
            h_range = (h_med - h_std * self.filter_rel_size_stdl[1], h_med + h_std * self.filter_rel_size_stdh[1])

        print("running 2nd single bee pass:")
        print("width:", w_med, w_std, w_range)
        print("height:", h_med, h_std, h_range)
        print("aspect ratio:", self.ar_range)

        for (i, c_data) in enumerate(self.computed):
            if c_data[0] is None or not c_data[1]: continue

            ellipse = c_data[0]
            w = ellipse[1][0]
            h = ellipse[1][1]
            ar = h / w
            
            print(f"single-bee check 2: {i, w, h, ar}")
            if self.ar_range[0] <= ar <= self.ar_range[1] \
            and w_range[0] <= w <= w_range[1] \
            and h_range[0] <= h <= h_range[1] :
                self.computed[i][2] = Counting.DETECT_SINGLE

        self.w_range = w_range
        self.h_range = h_range

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
                area = cv.contourArea(contour)
                single_bee_area_sum += area
                c_data[3] = area
            elif c_data[2] == Counting.DETECT_CLUMP:
                area = _contour_get_area_no_holes(self.contours, i, self.heirarchy)
                clump_area_sum += area
                c_data[3] = area

        bee_area_avg = single_bee_area_sum / single_bee_n if single_bee_n > 0 else 0
        self.bee_area_avg = bee_area_avg
        bee_n = single_bee_n + clump_area_sum / bee_area_avg if bee_area_avg > 0 else 0

        self.n_total = np.round(bee_n)
        self.n_single = single_bee_n
        return self.n_total

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
                n = status[3] / self.bee_area_avg
                cv.putText(self.img_draw, f"{n:.2f}", (bbox[0], bbox[1] - 4), cv.FONT_HERSHEY_COMPLEX, 0.5,(255,0,0),2,cv.LINE_AA)

    def _draw_rejected(self):
        for i, c_data, contour in zip(range(len(self.computed)), self.computed, self.contours):
            if c_data[0] is not None and c_data[2] == Counting.DETECT_NONE:
                bbox = cv.boundingRect(contour)
                ellipse = c_data[0]
                w = ellipse[1][0]
                h = ellipse[1][1]
                ar = h/w
                cv.rectangle(self.img_draw, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 0, 255), 1)
                cv.putText(self.img_draw, f"{i}, ar:{ar:.2f},w:{w:.2f},h:{h:.2f}, ext:{c_data[1]}", (bbox[0], bbox[1] - 4), cv.FONT_HERSHEY_COMPLEX, 0.5,(0,0,255),2,cv.LINE_AA)

    def _draw_ellipses(self):
        pass

    

## TESTING ##
if __name__ == "__main__" and RUN_TESTS:
    img = cv.imread("images/bee-image-samples/bee-image-8.jpg")
    if img is None:
        raise RuntimeError("Image file cannot be read.")
    
    settings = CountingSettings('userdata/counting_settings.json')

    settings.refresh()
    settings.print()
    counting = Counting(img, settings)
    settings.refresh()  # force to save here

    counting._preprocess()
    cv.imwrite('temp/preprocessed.jpg', counting.img_bgr)
    cv.imshow("out", counting.img_bgr)
    cv.waitKey(0)
    

    counting._get_shapes()
    cv.imshow("out", cv.cvtColor(counting.img_bin, cv.COLOR_GRAY2BGR))
    cv.waitKey(0)

    counting._filter_single_bees_rel()
    counting._filter_clumps()
    bee_n = counting._get_count()
    print(f"Total bees: {bee_n}")
    print(f"Identified single bees: {counting.n_single}")

    counting._draw_init()
    counting._draw_contours()
    counting._draw_single_bees()
    counting._draw_clumps()
    counting._draw_rejected()
    cv.imshow("out", counting.img_draw)
    cv.waitKey(0)

    
    


    cv.destroyAllWindows()