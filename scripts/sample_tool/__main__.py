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


import argparse

from images import ImageIndex
import logic

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
    
    subparsers = parser.add_subparsers(dest="command", required=True)

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