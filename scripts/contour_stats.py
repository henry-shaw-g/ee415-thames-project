from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

from counting.algorithm import algorithm
from counting.contour import Contour
from counting.image import Image
from counting import render_output

# n dimensional histogram bin
class BinsND:
    '''
    constructor:
    input:
        bin_dims: dict of {key: (start, end, num_bins)}
    '''
    def __init__(self, bin_dims):
        # documenting this would be too much work
        shape = [bin_dim[2] for _, bin_dim in bin_dims.items()]
        self.index = {key: i for (i, (key, _)) in enumerate(bin_dims.items())}
        self.bin_edges = [np.linspace(bin_dim[0], bin_dim[1], bin_dim[2] + 1) for _, bin_dim in bin_dims.items()]
        self.ranges = [(bin_dim[0], bin_dim[1]) for _, bin_dim in bin_dims.items()]
        self.bins = np.zeros(shape, dtype=np.double)

    '''
    add a set of data into the histogram (the data would be from N series)
    input:
        arrays: dict of {key: np.array}
    '''
    def add(self, arrays):
        arrays = [arrays[key] for key in self.index]
        (bins_to_add, _) = np.histogramdd(arrays, bins=self.bin_edges, range=self.ranges, density=False)
        self.bins += bins_to_add

    def get_hist1D(self, key):
        idx = self.index[key]
        return self.bins.sum(axis=tuple(i for i in range(len(self.bins.shape)) if i != idx))
    
    def get_hist2D(self, key1, key2):
        idx1 = self.index[key1]
        idx2 = self.index[key2]
        return self.bins.sum(axis=tuple(i for i in range(len(self.bins.shape)) if i != idx1 and i != idx2))
    
    def get_barplot_edges(self, key):
        idx = self.index[key]
        edges = self.bin_edges[idx]
        return (edges[1:] + edges[:-1]) / 2

# take 1 picture as input

image_containers = [
    r"C:\Users\henry\OneDrive - Washington State University (email.wsu.edu)\WSU\projects\EE4156_BeeSampleImages\input_batch_1",
    r"C:\Users\henry\OneDrive - Washington State University (email.wsu.edu)\WSU\projects\EE4156_BeeSampleImages\input_batch_2",
    ]


# area_bin = np.zeros(20)
# AR_bin = np.zeros(10)
# ellipse_fit_bin = Bin(0.0, 2.0, 20)
# area_normalized_bin = np.zeros(10)

bins = BinsND({
    "area_normalized_median": (0.0, 4.0, 25),
    "AR": (0.0, 5.0, 50),
    "ellipse_fit": (0.0, 2.0, 50),
})

image_paths = []

for container in image_containers:
    import os
    image_files = [f for f in os.listdir(container) if os.path.isfile(os.path.join(container, f))]
    image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
    image_files = [os.path.join(container, f) for f in image_files]
    print(f"Found {len(image_files)} images in {container}")

    for image_path in image_files:
        print(f"Adding image {image_path} to processing queue.")
        image_paths.append(image_path)

for image_path in image_paths:
    print(f"Processing image {image_path}")
    output = algorithm(image_path, settings_path=None)
    contours = output.contours
    contour_list = contours.contours
    for contour in contours.contours:
        print(contour.get_type(), contour.area)
    reasonable = list(filter(lambda c: 100 < c.area < 1e5 and c.get_type() != Contour.type.rejected, contour_list))

    if False:
        img = output.image_handle.get_image(Image.type.OUTPUT)
        img = render_output.render_output(img, reasonable, {})
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        plt.figure()
        plt.imshow(img)
        plt.axis('off')
        plt.show()

    # print(sum(1 for _ in filter(lambda c: c.get_type() == Contour.type.single_bee ,contours.contours)))

    # making histogram of all resolution / scale invariant observables of bee contours
    areas = np.array([contour.area for contour in reasonable])
    area_median = np.median(areas)
    areas_normalized = areas / area_median
    ARs = np.array([contour.fitted_rect_aspect_ratio for contour in reasonable])
    ellipse_areas = np.array([contour.fitted_ellipse_area for contour in reasonable])
    ellipse_fit = np.divide(areas, ellipse_areas) # closer to 1 = better? 

    bins.add({
        "area_normalized_median": areas_normalized,
        "AR": ARs,
        "ellipse_fit": ellipse_fit,
    })

plt.figure()

plt.subplot(221)
plt.title("area normalized by median")
areas_normalized_bin = bins.get_hist1D("area_normalized_median")
areas_normalized_edges = bins.get_barplot_edges("area_normalized_median")
plt.bar(areas_normalized_edges, areas_normalized_bin, width=areas_normalized_edges[1]-areas_normalized_edges[0])

plt.subplot(222)
plt.title("aspect ratio")
AR_bin = bins.get_hist1D("AR")
AR_edges = bins.get_barplot_edges("AR")
plt.bar(AR_edges, AR_bin, width=AR_edges[1]-AR_edges[0])

plt.subplot(223)
plt.title("ellipse fit")
ellipse_fit_bin = bins.get_hist1D("ellipse_fit")
ellipse_fit_edges = bins.get_barplot_edges("ellipse_fit")
plt.bar(ellipse_fit_edges, ellipse_fit_bin, width=ellipse_fit_edges[1]-ellipse_fit_edges[0])

plt.subplot(224)
plt.title("AR vs ellipse fit")

ellipse_fit_vs_AR = bins.get_hist2D("AR", "ellipse_fit")
plt.imshow(ellipse_fit_vs_AR.T, origin='lower', aspect='auto', extent=(AR_edges[0], AR_edges[-1], ellipse_fit_edges[0], ellipse_fit_edges[-1]))
plt.colorbar(label='Counts')

plt.show()