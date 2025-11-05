'''

'''
import cv2 as cv
import numpy as np
from ultralytics import YOLO
from counting.contour import Contour
from counting.contour_merge import Merger

_loaded_cnn = None

def load(cnn_class, *args, **kwargs):
    global _loaded_cnn
    if _loaded_cnn:
        raise RuntimeError("CNNDetect class already loaded for this session.")
    
    _loaded_cnn = cnn_class(*args, **kwargs)
    return _loaded_cnn


def get():
    global _loaded_cnn
    if _loaded_cnn is None:
        raise RuntimeError("CNNDetect class has not been loaded for this session. Call cnn_detect.load with the appropriate parameters.")
    return _loaded_cnn

'''
class: CNN
    Wrapping class for loading data for the CNN (weights and architecture)
'''
class CNN:
    min_context_window_size = 300
    tile_context_window_size = 640

    def __init__(self):
        pass

    def infer_single_bees(self, cv_image):
        pass

class YoloV11SegCNN(CNN):
    min_context_window_size = 300
    tile_context_window_size = 640

    def __init__(self, path_to_weights):
        self._model = YOLO(path_to_weights)

    def infer_single_bees(self, cv_image):
        results = self._model(cv_image)[0]
        # boxes = results.boxes.xyxy.cpu().numpy()
        # Class IDs
        classes = results.boxes.cls.cpu().numpy()       # class ids
        probs = results.boxes.conf.cpu().numpy()        # confidence scores
        # masks = results.masks.data.cpu().numpy()  # shape: (N, H, W)
        if not results.masks:
            print("Warning, the masks result was none.")
            return [], []
        polygons = results.masks.xy
        for i in range(len(classes)):
            prob = probs[i]
            polygon = polygons[i]
            class_id = classes[i]
            if class_id != 0:
                print("Warning: detected non-bee class id (not expected): ", class_id)
                continue

            polygon = polygon.reshape((-1, 1, 2)).astype(np.int32)
            polygons[i] = polygon

        return polygons, probs



'''
class: CNNDetector
    Logical instance of detecting bees from a single image.
'''
class CNNDetector:
    bbox_reject_margin = 5

    def __init__(self, cnn, source_image):
        self._cnn = cnn
        self._source_image = source_image
        self._contours = []
        self._confidence_threshold = 0.7

    '''
    fn: process_contour_list
        Use a set of contours from the conventional algorithm and use those identified as clumps
        as the bounding boxes for the CNN to search in.
    '''
    def process_contour_list(self, contours):
        for contour in contours:
            if contour.get_type() == Contour.type.clump:
                self.detect_in_bbox(contour.bounding_box)
        return self._contours

    def process_bbox_list(self, bboxes):
        for bbox in bboxes:
            self.detect_in_bbox(bbox)
        # return contours at end
        return self._contours        


    def _iterate_tiles(self):
        image_h, image_w = self._source_image.shape[0:2]
        stride_overlap = 100
        step_size = self._cnn.tile_context_window_size - stride_overlap
        for y in range(0, image_h, step_size):
            for x in range(0, image_w, step_size):
                # define bbox
                bbox = (x, y, min(self._cnn.tile_context_window_size, image_w - x), min(self._cnn.tile_context_window_size, image_h - y))
                # ok this is pretty cool python
                yield bbox

    '''
    fn: process_by_tiles
        Divide the image into tiles and process each tile with the CNN, using the preferred context window size.
    '''
    def process_by_tiles(self):
        for bbox in self._iterate_tiles():
                # define bbox
                self.detect_in_bbox(bbox)
        return self._contours

    def debug_draw_tiles(self, image):
        for bbox in self._iterate_tiles():
            cv.rectangle(image, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (255,0,0), 2)


    # call this for all clumps w/ in the image
    def detect_in_bbox(self, bbox):
        # force bbox to be beyond minimum context window size
        image_h, image_w = self._source_image.shape[0:2]
        diffx = self._cnn.min_context_window_size - bbox[2]
        if diffx > 0:
            x_new = max(0, bbox[0] - diffx // 2)
            w_new = min(bbox[2] + diffx, image_w - x_new)
            bbox = (x_new, bbox[1], w_new, bbox[3])
        diffy = self._cnn.min_context_window_size - bbox[3]
        if diffy > 0:
            y_new = max(0, bbox[1] - diffy // 2)
            h_new = min(bbox[3] + diffy, image_h - y_new)
            bbox = (bbox[0], y_new, bbox[2], h_new)

        view = self._source_image.view()
        slice = view[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]  # y1:y2, x1:x2
        polygons, probs = self._cnn.infer_single_bees(slice)
        
        for (i, prob) in enumerate(probs):
            if prob < self._confidence_threshold:
                continue
            polygon = polygons[i]

            # reject polgyon if it has too many points on the border of the bbox
            border_point_count = 0
            for point in polygon:
                if point[0][0] <= self.bbox_reject_margin or point[0][0] >= bbox[2]-self.bbox_reject_margin or point[0][1] <= self.bbox_reject_margin or point[0][1] >= bbox[3]-self.bbox_reject_margin:
                    border_point_count += 1
            if border_point_count / len(polygon) > 0.01:
                continue

            #shift polygon coordinates to be relative to full image
            polygon += np.array([bbox[0], bbox[1]]).reshape((1,1,2))
            contour_obj = Contour(polygon, source="cnn")
            contour_obj.set_type(Contour.type.unprocessed)
            self._contours.append(contour_obj)
    

'''
temp:
    Henry's test code
'''
if __name__ == "__main__":
    import cv2 as cv
    from matplotlib import pyplot as plt
    import json
    import os
    weights_path = "data/bee_detect_yolov11seg.pt"
    load(YoloV11SegCNN, path_to_weights=weights_path)
    cnn = get()
    # test_image = "/Users/henryshaw/Library/CloudStorage/OneDrive-WashingtonStateUniversity(email.wsu.edu)/WSU/projects/EE4156_BeeSampleImages/input_batch_2/401-4-2-3.jpg"
    test_image = os.getenv("BEE_IMAGE_PATH")
    print("Loading file:", test_image)
    if not os.path.exists(test_image):
        raise FileNotFoundError(test_image)
    
    image = cv.imread(test_image)
    print("Loaded image shape: ", image.shape)

    # do detection with detector object
    detector = CNNDetector(cnn, image)
    bbox = (900, 900, 1400, 1400)
    detector.detect_in_bbox(bbox)
    contours = detector._contours

    # merge duplicates
    merger = Merger(image, contours, json.load(open("counting/default_settings.json")))
    merger._merge()
    

    # draw results
    for contour in detector._contours:
        if contour.get_type() == Contour.type.single_bee or (contour.get_type() == Contour.type.rejected and contour.source == "cnn"):
            rejected = contour.get_type() == Contour.type.rejected
            contour_line_thickness = 2 if rejected else 1
            contour_line_color = (0, 0, 255) if rejected else (0, 255, 0)
            cv.drawContours(image, [contour.contour], -1, contour_line_color, 1)
            cv.ellipse(image, 
                    (int(contour.fitted_rotated_rect[0][0]), int(contour.fitted_rotated_rect[0][1])), 
                    (int(contour.fitted_rect_width//2), int(contour.fitted_rect_height//2)), 
                    contour.fitted_rect_angle, 0, 360, (255, 100, 100), 1)
            cX, cY = contour.get_centroid()
            cv.putText(image, str(contour.id), (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    
    plt.imshow(cv.cvtColor(image, cv.COLOR_BGR2RGB))
    plt.show()