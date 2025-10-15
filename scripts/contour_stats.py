from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

from counting.algorithm import algorithm
from counting.contour import Contour
from counting.image import Image
from counting import render_output

# n dimensional histogram bin
class Bin:
    def __init__(self, bin_dims):
        # documenting this would be too much work
        shape = [bin_dim[2] for _, bin_dim in bin_dims]
        self.index = {key: [i, *bin_dim] for (i, key, bin_dim) in bin_dims}
        self.bins = np.ndarray(shape, dtype=np.int32)

        # self.n = n
        # self.bins = np.zeros(n)
        # self.min = s
        # width = (e - s) / n
        # self.max = n * width
        # self.bin_edges = np.arange(self.min, self.max + width / 2, width)

    def add_

    def count_add(self, array):
        (bins_to_add, _) = np.histogram(array, bins=self.bin_edges, range=(self.min, self.max))
        self.bins += bins_to_add


# take 1 picture as input
image_path = "/Users/henryshaw/Library/CloudStorage/OneDrive-WashingtonStateUniversity(email.wsu.edu)/WSU/projects/EE4156_BeeSampleImages/input_batch_1/bee-image-20.jpg"


area_bin = np.zeros(20)
AR_bin = np.zeros(10)
ellipse_fit_bin = Bin(0.0, 2.0, 20)
area_normalized_bin = np.zeros(10)

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
# normalize area by mean
ARs = np.array([contour.fitted_ellipse_aspect_ratio for contour in reasonable])
ellipse_areas = np.array([contour.fitted_ellipse_area for contour in reasonable])
ellipse_fit = np.divide(areas, ellipse_areas) # closer to 1 = better? 
ellipse_fit_bin.count_add(ellipse_fit)


plt.figure()
plt.subplot(221)
plt.title("area histogram (NOT INVARIANT)")
plt.hist(areas, bins = 25)
plt.yscale("log")
plt.subplot(222)
plt.title("AR histogram")
plt.hist(ARs, bins = 20)
plt.subplot(223)
plt.title("AR vs ellipse_fit")
plt.hist2d(ARs, ellipse_fit_bin.bins)
plt.colorbar()
plt.show()