'''
script: sample_tool.py
desc:
    CLI that does various automated tasks for pushing image slice training data from collected sample images.
    Not production so I don't care about organization or error handling too much.

structure of image index folder:
    root/
        image_index.json
        images/
            image0001.png
            image0002.png
            image0003.png
            ...
        
structure of slice index folder:
    root/
        slice_index.json
        queue/
            slice0001.png
            slice0002.png
            ...
'''

import os
from collections import namedtuple
import json
import shutil
import argparse

ImageInfo = namedtuple('ImageInfo', ['id', 'sliced_random', 'sliced_clump', 'slice_random_num', 'sliced_clump_num'])

'''
    class: ImageIndex
        Index of full-sample images. Keeps track of a unique id for each image
        and whether it has been sliced in random or clump modes.
'''
class ImageIndex():

    '''
    ctor
    args:
        index_root_path: path to root of image index folder
    desc:
        Creates image index object by checking folders and loading index file on disk.
    '''
    def __init__(self, index_root_path):
        # load index into memory for working with
        self.root_path = index_root_path
        self.index = {}
        self.index_counter = 0
        

    def load(self):
        # check directory structure
        if not os.path.exists(self.root_path):
            raise ValueError(f"Index root path does not exist: {self.root_path}")
        if not os.path.exists(os.path.join(self.root_path, 'image_index.json')):
            raise ValueError(f"Image index file does not exist in root path: {self.root_path}")
        if not os.path.exists(os.path.join(self.root_path, 'images')):
            raise ValueError(f"Images directory does not exist in root path: {self.root_path}")

        
        # read index file
        index_file_path = os.path.join(self.root_path, 'image_index.json')
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
                'sliced_random': d.get('sliced_random', False),
                'sliced_clump': d.get('sliced_clump', False)
            }
            self.index = {fill_defaults(item)['id']: ImageInfo(**fill_defaults(item)) for item in data.get('images', [])}
            self.index_counter = data.index_counter

    '''
    fn: save
    desc:
        Saves current index in memory back to disk.
    '''
    def save(self, *, alt_path=None, build_structure=False):
        save_root_path = alt_path if alt_path else self.root_path
        if build_structure:
            if not os.path.exists(save_root_path):
                os.makedirs(save_root_path, exist_ok=True)
            if not os.path.exists(os.path.join(save_root_path, 'images')):
                os.makedirs(os.path.join(save_root_path, 'images'), exist_ok=True)

        index_file_path = os.path.join(self.root_path, 'image_index.json')
        with open(index_file_path, 'w') as f:
            images = [info._asdict() for info in self.index.values()]
            data = {
                'index_counter': self.index_counter,
                'images': images
            }
            json.dump(data, f, indent=4)

    def push_images(self, image_paths):
        index_new = []
        counter_new = self.index_counter

        fail = False
        for image_path in image_paths:
            # check path exists
            if not os.path.exists(image_path):
                print(f"Image path does not exist: {image_path}")
                fail = True
                break
            
            # check is png
            if not os.path.isfile(image_path) or not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"Image path is not a valid image file (png/jpg/jpeg): {image_path}")
                fail = True
                break
            
            image_id = f"image{counter_new:04d}"
            info = ImageInfo(id=image_id, sliced_random=False, sliced_clump=False)
            # add to index
            counter_new += 1
            index_new.append(info)

        if fail:
            print("One or more images failed to process. No changes were made to the index.")
            return False
        
        self.index_counter = counter_new
        for image_path, info in zip(image_paths, index_new):
            self.index[info.id] = info
            dest_path = os.path.join(self.root_path, 'images', f"{info.id}{os.path.splitext(image_path)[1]}")
            shutil.copyfile(image_path, dest_path)
            print(f"Image {image_path} indexed as {info.id} and copied to {dest_path}")

        
# CLI interface
class CLIExecutor:
    def __init__(self, args):
        # global state btw
        self.args = args
        self.image_index = None
        self.slice_index = None

    def mk_image_index(self):
        self.image_index = ImageIndex(self.args.index_dir)
        self.image_index.save(build_structure=True)
        print(f"Image index created at {self.args.index_dir}")

    def mk_slice_index(self):
        pass

    def push_images(self):
        pass

    def slice_images(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = "sample_tool",
        description="Tool for indexxing sample images and extracting slices for annotation.",
    )
    
    subparsers = parser.add_subparsers()

    parser_mk_image_index = subparsers.add_parser("mk_image_index", help="Create a new image index structure.")
    parser_mk_image_index.add_argument("index_dir", help="Path to create the image index directory.")

    parser_mk_slice_index = subparsers.add_parser("mk_slice_index", help="Create a new slice index structure.")
    parser_mk_slice_index.add_argument("slice_dir", help="Path to create the slice index directory.")

    parser_push_images = subparsers.add_parser("push_images", help="Push new images to the index.")
    parser_push_images.add_argument("image_paths", nargs="+", help="Paths to the image files to add.")

    parser_slice_images = subparsers.add_parser("slice_images", help="Slice images in the index for annotation.")
    parser_slice_images.add_argument("index_dir", help="Path to the image index directory.")
    parser_slice_images.add_argument("slice_dir", help="Path to the slice index directory.")
    parser_slice_images.add_argument("--mode", choices=["all", "random", "clump"], required=True, help="Slicing mode to use.")
    parser_slice_images.add_argument("--range", type=str, help="Range of image ids to slice, e.g., 1-10.")

    args = parser.parse_args()
    executor = CLIExecutor(args)
    print(args)

    match args.command:
        case "mk_image_index":
            executor.mk_image_index()
        case "mk_slice_index":
            executor.mk_slice_index()
        case "push_images":
            executor.push_images()
        case "slice_images":
            executor.slice_images()
        case _:
            # i think arg parsing will catch this first
            print(f"Unknown command: {args.command}")