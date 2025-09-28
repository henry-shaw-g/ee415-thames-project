'''
logic.py
    Standalone functions for image slicing mostly.
'''

import random
import cv2 as cv
import numpy as np
from .slices import *
from .images import *

random.seed()
nprng = np.random.default_rng()

random_slice_params = {
    'slice_size_min': 256,
    'border_padding': 16,
    'num_slice_min': 5,
    'num_slice_max': 10
}

'''
class: FileModRecord
    Record of a file modification for undo/redo tracking.
'''
class FileModRecord():
    def __init__(self):
        self.creations = []
        # as of now only track creations
    
    '''
    fn: created
    '''
    def created(self, path):
        self.creations.append(path)

    '''
    fn: undo
    '''
    def undo(self):
        for path in self.creations:
            if os.path.exists(path):
                print(f"<FileModRecord.undo> aborting: removing created file at path: {path}")
                os.remove(path)
        self.creations = []

    '''
    fn: clear
    '''
    def clear(self):
        self.creations = []


'''
fn: gen_image_slices_random
    Randomly selects bounding boxes as slices from the input image.
inputs:
    image_path: path to image file
    image_id: id of the source image
outputs: List of SliceData objects for each slice.
'''
def gen_image_slices_random(image_path, image_id):
    # load image
    image = cv.imread(image_path)
    shape = image.shape
    if image is None: 
        raise ValueError(f"Failed to load image from path: {image_path}")

    n = random.randint(random_slice_params['num_slice_min'], random_slice_params['num_slice_max'])
    b = random_slice_params['border_padding']
    ss_min = random_slice_params['slice_size_min']
    ss_max = max(min(shape[0], shape[1]) // n * 3, ss_min)
    
    
    min_sep = min(ss_min, min(shape[0], shape[1]) // n) # allow for n slices to fit in image, even if they have some overlap.
    # bbx = np.ones(n, dtype=int) * -min_sep
    # bby = np.ones(n, dtype=int) * -min_sep
    bbw = (nprng.random(n) * (ss_max - ss_min) + ss_min).astype(int)
    bbh = (nprng.random(n) * (ss_max - ss_min) + ss_min).astype(int)
    bbx = (nprng.random(n) * (shape[1] - 2*b - bbw) + b).astype(int)
    bby = (nprng.random(n) * (shape[0] - 2*b - bbh) + b).astype(int)

    

    mk_slice_data = lambda i: SliceData(
        mode = 'random',
        source_image_id = image_id,
        bbox = (bbx[i], bby[i], bbw[i], bbh[i]),
        bitmap = image[bby[i]:(bby[i]+bbh[i]), bbx[i]:(bbx[i]+bbw[i])] # this is a VIEW not a copy
    )
    slices = list(map(mk_slice_data, range(n)))
    return image, slices, bbx, bby, bbw, bbh

'''
fn: gen_image_slices_clump
    Gets slices as bounding boxes of all detected clumps in the input image.
inputs:
    image_path: path to image file
    image_id: id of the source image
    counting_alg: session of counting algorithm to use (so dont have to reload heavy weight stuff every time)
outputs: List of SliceData objects for each slice.
'''
def gen_image_slices_clump(image_path, image_id, counting):
    # load image
    image = cv.imread(image_path)
    shape = image.shape
    if image is None: 
        raise ValueError(f"Failed to load image from path: {image_path}")
    
    raise NotImplementedError("Clump mode not implemented yet.")
    # TODO: call the counting algorithm which needs to have as output the bounding boxes of clumps

'''
fn: slice_image
    Slices an image using selected mode and pushes slices into index and updates image slice record in index.
'''
def slice_image(file_mod_record, image_index, slice_index, image_id, mode):
    path = image_index.get_image_path(image_id)

    if mode == "clump":
        raise NotImplementedError("Clump mode not implemented yet.")
    elif mode == "random":
        image, slices, *_ = gen_image_slices_random(path, image_id)
    else:
        raise ValueError(f"Unknown slice mode: {mode}")
    
    # push slices to index
    slice_index.push_slices(slices, file_mod_record)

    # can assume that no failures happened at this point
    if mode == "clump":
        image_index.replace_info(image_id, sliced_clump=True, sliced_clump_num=len(slices))
    elif mode == "random":
        image_index.replace_info(image_id, sliced_random=True, sliced_random_num=len(slices))


# testing
if __name__ == "__main__":
    path = "some_samples/bee-image-1.jpg"
    image, slices, *_ = gen_image_slices_random(path, "test-image-1")

    cv.imshow("source", image)
    cv.waitKey(0)

    for i, s in enumerate(slices):
        cv.imshow(f"slice-{i}", s.bitmap)
        cv.waitKey(0)
        print(s.bbox)
    cv.destroyAllWindows()

    
    
