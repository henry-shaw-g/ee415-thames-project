from collections import namedtuple
import os
import shutil
import json
import cv2 as cv

SLICE_INDEX_FILENAME = 'slice_index.json'

'''
    class: SliceInfo
        Record object for a slice in slice index.
'''
SliceInfo = namedtuple('SliceInfo', ['id', 'source_image_id', 'mode'])

'''
    class: SliceData
        Data for in memory slice being processed. Includes reference to image bitmap.
'''
SliceData = namedtuple('SliceData', ['source_image_id', 'mode', 'bitmap'])

'''
    class: SliceIndex
        Index of image slices for annotation. Keeps track of a unique id for each slice
        and which source image and mode it came from.
        Too lazy to think about doing clean inheritance with ImageIndex right now.
'''
class SliceIndex():
    '''
    ctor
    inputs:
        index_root_path: path to root of slice index folder
    '''
    def __init__(self, index_root_path):
        self.root_path = index_root_path
        self.index = {}
        self.index_counter = 0

    '''
    fn: load
    desc: Validates the directory structure and then loads the slice index from disk.
    '''
    def load(self):
        # check directory structure
        if not os.path.exists(self.root_path):
            raise ValueError(f"Index root path does not exist: {self.root_path}")
        if not os.path.exists(os.path.join(self.root_path, SLICE_INDEX_FILENAME)):
            raise ValueError(f"Slice index file does not exist in root path: {self.root_path}")
        if not os.path.exists(os.path.join(self.root_path, 'queue')):
            raise ValueError(f"Slice index queue directory does not exist in root path: {self.root_path}")

        # read index file
        index_file_path = os.path.join(self.root_path, SLICE_INDEX_FILENAME)
        # backup index file
        root_path, ext = os.path.splitext(index_file_path)
        backup_path = root_path + "_backup" + ext
        shutil.copyfile(index_file_path, backup_path)

        with open(index_file_path, 'r') as f:
            import json
            data = json.load(f)
            # Fill missing keys with defaults using a lambda
            fill_defaults = lambda d: {
                'id': d['id'], # will need to errror if id is missing
                'mode': d.get('mode', 'unknown'),
                'source_image_id': d.get('source_image_id', None)
            }
            self.index = {fill_defaults(item)['id']: SliceInfo(**fill_defaults(item)) for item in data.get('images', [])}
            self.index_counter = data.index_counter
    
    '''
    fn: save
    desc: Saves the slice index to disk.
        Note that the alt_path and build_structure inputs are not implemented yet.
    '''
    def save(self, *, alt_path=None, build_structure=False):
        save_root_path = self.root_path
        index_file_path = os.path.join(save_root_path, SLICE_INDEX_FILENAME)
        with open(index_file_path, 'w') as f:
            slices = [info._asdict() for info in self.index.values()]
            data = {
                'index_counter': self.index_counter,
                'slices': slices
            }
            json.dump(data, f, indent=4)

    '''
    fn: push_slices
    desc: Adds new slices from a list of slice data objects to indexs and saves the bitmaps as images to disk.
    inputs:
        slices: list of SliceData objects. Note that the bitmap field will most likely be np array VIEW as opposed to copy.
            The format of the bitmap must be uint8 3 channel BGR (OpenCV standard).
    '''
    def push_slices(self, slices):
        # will just let this fail chaotically for now
        for slice_data in slices:
            slice_info = SliceInfo(
                id=self.index_counter,
                source_image_id=slice_data.source_image_id,
                mode=slice_data.mode
            )
            self.index[self.index_counter] = slice_info
            self.index_counter += 1

            # Save the bitmap as an image
            bitmap = slice_data.bitmap
            image_path = os.path.join(self.root_path, 'queue', f"slice{self.index_counter}.png")
            cv.imwrite(image_path, bitmap)