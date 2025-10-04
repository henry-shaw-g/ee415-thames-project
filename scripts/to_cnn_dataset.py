'''
module: to_cnn_dataset
    CLI tool to extract images and whatever label format was used for annotation and copies everything into a new folder
    with specific label format and structure for CNN training.
'''
import random
import os
import shutil
import argparse
from PIL import Image

CAN_WRITE = True

# intermediate representation
class Interm():
    def __init__(self):
        self.images = [] # list of image file paths
        self.class_set = set()
        self.labels_class = [] # in memory label classes
        self.labels_pts = [] # in memory label points (support bbox, segment polygons, idk...)

# pulling functions
# i.e extract images and labels into intermediate form in memory
# def pull_COCO_like_seg(image_files, labels_are_siblings = True):
#     print("Pulling COCO-like segmentation annotations...")
#     interm = Interm()
#     interm.images = image_files.copy()
#     for img_fp in image_files:
#         print("Pulling image:", img_fp)
#         if labels_are_siblings:
#             lbl_fp = os.path.splitext(img_fp)[0] + '.json'
#         else:
#             raise NotImplementedError("Currently only supports sibling json files for COCO-like annotations.")
#         print("Pulling label:", lbl_fp)
#         # read json file and extract labels
#         import json
#         with open(lbl_fp, 'r') as f:
#             data = json.load(f)
#             for ann in data['annotations']:
#                 interm.labels_class.append(data['categories'][ann['category_id']]['name'])
#                 interm.labels_pts.append(ann['segmentation']) # assuming segmentation is in COCO format
#     return interm

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
            labels_class_list = []
            labels_pts_list = []
            interm.labels_class.append(labels_class_list)
            interm.labels_pts.append(labels_pts_list)
            for shape in data['shapes']:
                interm.class_set.add(shape['label'])
                labels_class_list.append(shape['label'])
                labels_pts_list.append(shape['points']) # assuming points is a list of [x, y] pairs
    return interm

# pushing functions
# i.e write images and labels to disk in specific structure
def push_YOLO_seg(interm, out_dir, p_train=0.75):
    print("Pushing to YOLO segmentation format...")
    print("Making output directory structure in :", out_dir)
    # make a train and val folder
    if CAN_WRITE:
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(os.path.join(out_dir, 'train'), exist_ok=True)
        os.makedirs(os.path.join(out_dir, 'val'), exist_ok=True)
        os.makedirs(os.path.join(out_dir, 'train', 'images'), exist_ok=True)
        os.makedirs(os.path.join(out_dir, 'train', 'labels'), exist_ok=True)
        os.makedirs(os.path.join(out_dir, 'val', 'images'), exist_ok=True)
        os.makedirs(os.path.join(out_dir, 'val', 'labels'), exist_ok=True)

    class_names = list(interm.class_set)
    class_index = {name: idx for idx, name in enumerate(class_names)}

    # make data.yaml file
    if CAN_WRITE:
        with open(os.path.join(out_dir, 'data.yaml'), 'w') as f:
            f.write('train: train/images\n')
            f.write('val: val/images\n')
            f.write(f'nc: {len(class_names)}\n')
            f.write('names: [')
            f.write(', '.join([f"'{i}'" for i in class_names]))
            f.write(']\n')

    N = len(interm.images)
    N_train = int(N * p_train)
    print(f"\nDataset split: {N_train} images for training, {N - N_train} images for validation.\n")

    # this is probably really inefficient but whatever

    images, labels_class, labels_pts = [None]*N, [None]*N, [None]*N
    reindex = list(range(N))
    random.seed()
    random.shuffle(reindex)
    for old_i, new_i in enumerate(reindex):
        images[new_i] = interm.images[old_i]
        labels_class[new_i] = interm.labels_class[old_i]
        labels_pts[new_i] = interm.labels_pts[old_i]

    for i in range(N):
        print(f"seg @ {i}:", labels_pts[i])

    i = 0
    for img_fp, cls_list, pts_list in zip(images, labels_class, labels_pts):
        dest = 'train' if i < N_train else 'val'
        i += 1
        img_fp_new = os.path.join(out_dir, dest, 'images', os.path.basename(img_fp))
        with Image.open(img_fp) as img:
            width, height = img.size
        print("Pushing image:", img_fp_new)
        if CAN_WRITE:
            shutil.copy(img_fp, img_fp_new)
        
        lbl_fp = os.path.join(out_dir, dest, 'labels', os.path.splitext(os.path.basename(img_fp_new))[0] + '.txt')
        lines = []
        print("Pushing label:", lbl_fp)
        # print("Class:", cls_list)
        # print("pts:", pts_list)
        # assuming seg is a list of lists (polygons)
        for cls, polygon in zip(cls_list, pts_list):
            cls_id = class_index[cls]
            xs = [point[0] for point in polygon]
            ys = [point[1] for point in polygon]
            line = f"{cls_id} " + "".join([f"{x/width:.6f} {y/height:.6f} " for x, y in zip(xs, ys)]) + "\n"
            lines.append(line)

        if CAN_WRITE:
            with open(lbl_fp, 'w') as f:
                f.writelines(lines)


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
        # interm = pull_COCO_like_seg(image_files)
        raise NotImplementedError("COCO format not yet implemented.")
    elif args.in_format == 'labelme':
        interm = pull_labelme_seg(image_files)
    else:
        raise ValueError("Unsupported annotation format.")

    # push to desired CNN training format
    push_YOLO_seg(interm, args.output_dir)