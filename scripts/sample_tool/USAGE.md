# Quick reference for sample_tool usage

## How to create image index directory:
With the working directory as this repo root:
```
python -m scripts.sample_tool mk_image_index {target_directory}
```

## How to create sample index directory:
Note implemented.

## How to push a batch of images
Assume working direcotry is this repo root.
The image index directory must have been created like above, with the path name known.
```
python -m scripts.sample_tool push_images {image_index_directory} {glob path of images}
```

Actual example:
```
python -m scripts.sample_tool push_images ~/thames_sample_images sample_batch_1/*.jpg
```

## How to slice images in index
```
python -m scripts.sample_tool slice_images {image_index_directory} {slice_index_direcotry} [optionally: --mode={random|clump}--range min-max]
```
Range is the numeric part of the ids. For example: 10-100 (idk why you would do this).

**Clump slicing is not supported** until we get the algorithm code rewritten.

Actual example:

```
python -m scripts.sample_tool slice_images ~/thames_sample_images ~/thames_slice_images
```