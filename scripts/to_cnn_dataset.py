'''
module: to_cnn_dataset
    CLI tool to extract images and whatever label format was used for annotation and copies everything into a new folder
    with specific label format and structure for CNN training.
'''
import os
import shutil
import argparse
from PIL import Image

# intermediate representation
class Interm():
    def __init__(self):
        self.images = [] # list of image file paths
        self.labels_class = [] # in memory label classes
        self.labels_pts = [] # in memory label points (support bbox, segment polygons, idk...)

# pulling functions
# i.e extract images and labels into intermediate form in memory
def pull_COCO_like_seg(image_files, labels_are_siblings = True):
    print("Pulling COCO-like segmentation annotations...")
    interm = Interm()
    interm.images = image_files.copy()
    for img_fp in image_files:
        print("Pulling image:", img_fp)
        if labels_are_siblings:
            lbl_fp = os.path.splitext(img_fp)[0] + '.json'
        else:
            raise NotImplementedError("Currently only supports sibling json files for COCO-like annotations.")
        print("Pulling label:", lbl_fp)
        # read json file and extract labels
        import json
        with open(lbl_fp, 'r') as f:
            data = json.load(f)
            for ann in data['annotations']:
                interm.labels_class.append(data['categories'][ann['category_id']]['name'])
                interm.labels_pts.append(ann['segmentation']) # assuming segmentation is in COCO format
    return interm

def pull_labelme_seg(image_files, labels_are_siblings = True):
    print("Pulling LabelMe segmentation annotations...")
    interm = Interm()
    interm.images = image_files.copy()
    for img_fp in image_files:
        print("Pulling image:", img_fp)
        if labels_are_siblings:
            lbl_fp = os.path.splitext(img_fp)[0] + '.json'
        else:
            raise NotImplementedError("Currently only supports sibling json files for LabelMe annotations.")
        print("Pulling label:", lbl_fp)
        # read json file and extract labels
        import json
        with open(lbl_fp, 'r') as f:
            data = json.load(f)
            for shape in data['shapes']:
                interm.labels_class.append(shape['label'])
                interm.labels_pts.append(shape['points']) # assuming points is a list of [x, y] pairs
    return interm

# pushing functions
# i.e write images and labels to disk in specific structure
def push_YOLO_seg(interm, out_dir):
    print("Pushing to YOLO segmentation format...")
    print("Making output directory structure in :", out_dir)
    # make a train and val folder
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'train'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'val'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'train', 'images'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'train', 'labels'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'val', 'images'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'val', 'labels'), exist_ok=True)
    # make dump folder so user can move images + labels into train and val as they wish
    os.makedirs(os.path.join(out_dir, 'dump'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'dump', 'images'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'dump', 'labels'), exist_ok=True)
    # make data.yaml file
    with open(os.path.join(out_dir, 'data.yaml'), 'w') as f:
        f.write('train: train/images\n')
        f.write('val: val/images\n')
        f.write(f'nc: {len(set(interm.labels_class))}\n')
        f.write('names: [')
        f.write(', '.join([f"'{i}'" for i in set(interm.labels_class)]))
        f.write(']\n')
    # copy images and labels to dump folder
    for img_fp in interm.images:
        img_fp_new = os.path.join(out_dir, 'dump', 'images', os.path.basename(img_fp))
        shutil.copy(img_fp, img_fp_new)
        print("Pushing image:", img_fp_new)
        with Image.open(img_fp) as img:
            width, height = img.size
        lbl_fp = os.path.join(out_dir, 'dump', 'labels', os.path.splitext(os.path.basename(img_fp_new))[0] + '.txt')
        with open(lbl_fp, 'w') as f:
            print("Pushing label:", lbl_fp)
            for cls, seg in zip(interm.labels_class, interm.labels_pts):
                cls_id = list(set(interm.labels_class)).index(cls)
                # assuming seg is a list of lists (polygons)
                for polygon in seg:
                    x_coords = polygon[0::2]
                    y_coords = polygon[1::2]
                    x_min = min(x_coords)
                    x_max = max(x_coords)
                    y_min = min(y_coords)
                    y_max = max(y_coords)
                    x_center = (x_min + x_max) / 2 / width
                    y_center = (y_min + y_max) / 2 / height
                    bbox_width = (x_max - x_min) / width
                    bbox_height = (y_max - y_min) / height
                    f.write(f"{cls_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert annotated dataset to CNN training format.")
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing images and annotations.')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save the CNN training dataset.')
    parser.add_argument('--in_format', type=str, choices=['coco', 'labelme'], required=True, help='Format of the annotations.')
    args = parser.parse_args()

    # gather image files
    image_files = []
    for root, _, files in os.walk(args.input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
    
    # pull annotations into intermediate representation
    if args.in_format == 'coco':
        interm = pull_COCO_like_seg(image_files)
    elif args.in_format == 'labelme':
        interm = pull_labelme_seg(image_files)
    else:
        raise ValueError("Unsupported annotation format.")

    # push to desired CNN training format
    push_YOLO_seg(interm, args.output_dir)