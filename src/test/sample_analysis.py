'''
Looking at various histograms of the image samples.
Main goal of this is to figure out how to optimally detect the rear part of the bee (bombaclat hehe)
Note: cwd is intended to be the root of the project.
'''

import numpy as np
import cv2 as cv
import os
import sys
import glob
import matplotlib.pyplot as plt

if not ('src' in sys.path):
    sys.path.append('src')

from util import color_mod, color_depth, masking

sample_dir = 'images/bee-image-samples'
sample_files = glob.glob(sample_dir + '/bee-image-[0-9].jpg') + glob.glob(sample_dir + '/bee-image-[0-9].png')
# sample_files = [sample_dir + '/bee-image-4.jpg']
# sample_files = ['src/test/in/bee-image-4-exposed.png']

hue_bin = np.zeros((180, 1), dtype=np.float32)
sat_bin = np.zeros((256, 1), dtype=np.float32)
val_bin = np.zeros((256, 1), dtype=np.float32)
gray_bin = np.zeros((256, 1), dtype=np.float32)

sat_hue_bin = np.zeros((10, 10), dtype=np.float32)
sat_val_bin = np.zeros((10, 10), dtype=np.float32)

sat_ranges = [(100, 200)]
hue_ranges = [(0, 255)]
val_ranges = [(50, 255)]

morph_kernel_1 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))

for sample_file in sample_files:
    img = cv.imread(sample_file)

    img = cv.resize(img, None, None, fx=0.3, fy=0.3, interpolation=cv.INTER_CUBIC)
    img = cv.GaussianBlur(img, (3, 3), 0)
    # img = color_mod.delocalize_brightness(img, (201, 201))
    img = color_mod.expose_piecewise_std(img)

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    hue_bin += cv.calcHist([hsv], [0], None, [180], [0, 180])
    sat_hist = cv.calcHist([hsv], [1], None, [256], [0, 256])
    sat_bin += sat_hist
    val_hist = cv.calcHist([hsv], [2], None, [256], [0, 256])
    val_bin += val_hist
    gray_bin += cv.calcHist([gray], [0], None, [256], [0, 256])

    Dsat_hue_bin, _, _ = np.histogram2d(hsv[:, :, 1].flatten(), hsv[:, :, 0].flatten(), bins=[10, 10], range=[[0, 255], [0, 180]])
    sat_hue_bin += Dsat_hue_bin

    Dsat_val_bin, _, _ = np.histogram2d(hsv[:, :, 1].flatten(), hsv[:, :, 2].flatten(), bins=[10, 10], range=[[0, 255], [0, 255]])
    sat_val_bin += Dsat_val_bin


    # attempt to higlight bee booty
    # first, estimate the bee-pixel percentage by value percentiling:
    p = np.sum(val_bin[0:128]) / np.sum(val_bin[0:256])
    print(f"bee pixel percentage: {p}")

    # use that to pickout saturation minimum (somewhat tigher than the bee percentage)
    sat_min = int(np.percentile(hsv[:, :, 1], 100 - p * 0.8* 100))
    print(sat_min)

    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    for sr, hr, vr in zip(sat_ranges, hue_ranges, val_ranges):
        Dmask = cv.inRange(hsv, (hr[0], sat_min, vr[0]), (hr[1], 255, vr[1]))
        mask = cv.bitwise_or(mask, Dmask)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, morph_kernel_1)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, morph_kernel_1)
    mask_dst = cv.distanceTransform(mask, cv.DIST_L1, maskSize=3)
    mask = cv.inRange(mask_dst, 4, 255)

    masked = masking.overlay_mask(img, mask, (0, 255, 0))
    

    # save individual saturation histograms
    plt.figure(1)
    plt.subplot(211)
    plt.plot(sat_hist)
    plt.yscale('log')
    plt.title('saturation histogram')
    plt.subplot(212)
    plt.plot(val_hist)
    plt.yscale('log')
    plt.title('value histogram')
    plt.savefig('src/test/out/sat_hist' + os.path.basename(sample_file) + '.png')
    plt.close()


    cv.imshow('img', masked)
    cv.waitKey(0)

    print(f"Got histograms or {sample_file}.")
cv.destroyAllWindows()

print("Finished getting histograms.")

print("showing 1dim histograms")

plt.figure(1, figsize=(12, 8))
plt.subplot(2, 2, 1)
plt.plot(hue_bin, color='r')
plt.yscale('log')
plt.title('Hue Histogram')
plt.xlim([0, 180])

plt.subplot(2, 2, 2)
plt.plot(sat_bin, color='g')
plt.yscale('log')
plt.title('Saturation Histogram')
plt.xlim([0, 256])

plt.subplot(2, 2, 3)
plt.plot(val_bin, color='b')
plt.yscale('log')
plt.title('Value Histogram')
plt.xlim([0, 256])

plt.subplot(2, 2, 4)
plt.plot(gray_bin, color='k')
plt.yscale('log')
plt.title('Gray Histogram')
plt.xlim([0, 256])


print("showing 2dim histograms")
plt.figure(2, figsize=(12, 8))
sat_hue_bin_log = np.log10(sat_hue_bin + 1)
plt.imshow(sat_hue_bin_log, interpolation='nearest', cmap='hot')
plt.title('Saturation vs Hue Histogram Log Count')
plt.xlabel('Hue')
plt.ylabel('Saturation')
plt.colorbar(label='Count')

plt.figure(3, figsize=(12, 8))
sat_val_bin_log = np.log10(sat_val_bin + 1)
plt.imshow(sat_val_bin_log, interpolation='nearest', cmap='hot')
plt.title('Saturation vs Value Histogram Log Count')
plt.xlabel('Value')
plt.ylabel('Saturation')
plt.colorbar(label='Count')


plt.show()
