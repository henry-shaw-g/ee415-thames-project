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

TODO:
    - If available, use exif data and/or some kind hasing of image bytes to avoid pushing duplicate images.
'''


import argparse
import glob
from .images import ImageIndex
from . import logic

# CLI interface
class CLIExecutor:
    def __init__(self, args):
        # global state btw
        self.args = args
        self.image_index = None
        self.slice_index = None
        self.file_mod_record = logic.FileModRecord()

    '''
    fn: mk_image_index
    '''
    def mk_image_index(self):
        self.image_index = ImageIndex(self.args.index_dir)
        self.image_index.save(build_structure=True)
        print(f"Image index created at {self.args.index_dir}")

    '''
    fn: mk_slice_index
    '''
    def mk_slice_index(self):
        raise NotImplementedError()

    '''
    fn: push_images
    '''
    def push_images(self):
        # get input paths
        input_path_str = self.args.image_path
        if not input_path_str:
            raise ValueError("No input image paths provided.")
        
        paths = glob.glob(input_path_str, recursive=False)
        print("slicing images at paths:")
        for p in paths:
            print(f" - {p}")

        if not paths:
            raise ValueError(f"No files found matching input path: {input_path_str}")
        
        self.image_index = ImageIndex(self.args.index_dir)
        self.image_index.load()

        try:
            self.image_index.push_images(paths, self.file_mod_record)
            self.image_index.save()
            self.file_mod_record.clear() # todo: save this state also ...
            print(f"Image index saved at {self.args.index_dir}")
        except Exception as e:
            print(f"Error occurred during push_images: {e}. UNDOING CHANGES.")
            self.file_mod_record.undo()
            print("CHANGES UNDONE.")
            raise e


    '''
    fn: slice_images
    '''
    def slice_images(self):
        self.image_index = ImageIndex(self.args.index_dir)
        self.image_index.load()
        self.slice_index = logic.SliceIndex(self.args.slice_dir)
        self.slice_index.load()

        iter = self.image_index.index.items()
        if self.args.range:
            split = self.args.range.split('-')
            nums = range(int(split[0]), int(split[1]) + 1)
            ids = (f'image{id:04d}' for id in nums if f'image{id:04d}' in self.image_index.index)
            iter = ((id, self.image_index.get_info(id)) for id in ids)

        for image_id, info in iter:
            if self.args.mode == 'random' and info.sliced_random:
                print(f"Skipping image id {image_id} with filename {info.filename} (already sliced with random mode)")
                continue
            if self.args.mode == 'clump' and info.sliced_clump:
                print(f"Skipping image id {image_id} with filename {info.filename} (already sliced with clump mode)")
                continue

            print(f"Slicing image id {image_id} with filename {info.filename}")
            try:
                logic.slice_image(self.file_mod_record, self.image_index, self.slice_index, image_id, self.args.mode)
            except Exception as e:
                print(f"Error occurred while slicing image {image_id}: {e}. UNDOING CHANGES")
                self.file_mod_record.undo()
                print("CHANGES UNDONE.")
                raise e
            
        # in an ideal world, these would both only run if the other succeded, but that would violate causality (?)
        print("Slicing operation complete, saving image and slice indices.")
        self.image_index.save()
        self.slice_index.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = "sample_tool",
        description="Tool for indexxing sample images and extracting slices for annotation.",
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_mk_image_index = subparsers.add_parser("mk_image_index", help="Create a new image index structure.")
    parser_mk_image_index.add_argument("index_dir", help="Path to create the image index directory.")

    parser_mk_slice_index = subparsers.add_parser("mk_slice_index", help="Create a new slice index structure.")
    parser_mk_slice_index.add_argument("slice_dir", help="Path to create the slice index directory.")

    parser_push_images = subparsers.add_parser("push_images", help="Push new images to the index.")
    parser_push_images.add_argument("index_dir", help="Path to the image index directory.")
    parser_push_images.add_argument("image_path", help="Path or glob to the image files to add.")

    parser_slice_images = subparsers.add_parser("slice_images", help="Slice images in the index for annotation.")
    parser_slice_images.add_argument("index_dir", help="Path to the image index directory.")
    parser_slice_images.add_argument("slice_dir", help="Path to the slice index directory.")
    parser_slice_images.add_argument("--mode", choices=["all", "random", "clump"], required=True, help="Slicing mode to use.")
    parser_slice_images.add_argument("--range", type=str, help="Range of image ids to slice, e.g., 1-10.")

    args = parser.parse_args()
    executor = CLIExecutor(args)

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