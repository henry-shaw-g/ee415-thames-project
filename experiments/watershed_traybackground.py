from glob import glob
import random
import cv2 as cv
import numpy as np

global stacking
stacking = False

''' display functions '''
def show_image(image, title="image", downscale=1, stack=False):
    if downscale != 1:
        width = int(image.shape[1] / downscale)
        height = int(image.shape[0] / downscale)
        image = cv.resize(image, (width, height))
    cv.imshow(title, image)
    if not stack:
        global stacking
        stacking = False
        cv.waitKey(0)
        cv.destroyAllWindows()
    elif stack:
        stacking = True

def close_images_at_end():
    if stacking:
        cv.waitKey(0)
        cv.destroyAllWindows()

''' image processing functions'''
def reduce_depth(image, bits=4):
    shift = 8 - bits
    image_reduced = np.right_shift(image, shift)
    image_reduced = np.left_shift(image_reduced, shift)
    return image_reduced

def equalize_spatial(channel):
    # assume 8 bit
    alpha = 1
    kernel_size = 128
    average_kernel = (kernel_size, kernel_size)
    average = cv.filter2D(channel, -1, np.ones(average_kernel, np.float32) / (kernel_size * kernel_size))
    return cv.addWeighted(channel, 1 + alpha, average, -alpha, 0)

def expose_piecewise_std(image, p1=0.4, p2=2):
        # self.previous_image = self.current_image.copy()
        # Create a lookup table for piecewise linear exposure adjustment
        lut = np.arange(256, dtype=np.float32) / 255.0
        # p1 = 0.4    # Control point (0 < p1 < 1)
        # p2 = 2      # Exposure multiplier for dark regions (p2 > 1)
        sep = int(p1 * 255)
        
        # Apply different exposure levels to dark and bright regions
        # brighten dark regions with a power-law (gamma) correction
        # Use gamma = 1/p2 so p2 > 1 brightens shadows
        gamma = 1.0 / p2 if p2 > 0 else 1.0
        lut[:sep] = np.power(lut[:sep], gamma)
        lut[sep:] += lut[sep-1] - lut[sep]  # Smoothly transition to bright regions
        
        # Ensure values stay in valid range [0,1] and convert back to uint8
        lut = (np.clip(lut, 0, 1) * 255.0).astype(np.uint8)
        
        return cv.LUT(image, lut)

''' main code'''

image_paths = glob(r"C:\Users\henry\OneDrive - Washington State University (email.wsu.edu)\WSU\EE4156\Suchting, Zachery's files - 415 Documents\25 Nov 4 Counting Session\*.png")
image_path = random.choice(image_paths) # to minimize bias while iterating
image = cv.imread(image_path)

image = expose_piecewise_std(image, 0.3, 1.5)
image = cv.GaussianBlur(image, (7, 7), 0)
show_image(image, "Original Image", downscale=3, stack=True)

image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

image_s = image_hsv[:, :, 1]
# make an average filter to normalize saturation to its neighbors
image_s_blurred = cv.blur(image_s, (256, 256))

# show_image(reduce_depth(image_s), "Saturation Channel", downscale=3, stack=True)
# show_image(image_s_blurred, "Blurred Saturation Channel", downscale=3, stack=True)

image_v = image_hsv[:, :, 2]
image_v = equalize_spatial(image_v)
show_image(image_v, "Value Channel", downscale=3, stack=True)

image_h = image_hsv[:, :, 0]
# show_image(image_h, "Hue Channel", downscale=3)

s0 = 32
alpha = 1
mask_sat_reject = image_s > s0 + alpha * image_s_blurred
# show_image(mask_sat_reject.astype(np.uint8) * 255, "Low Saturation Mask", downscale=3, stack=True)

# mask_value_reject = image_v < 64
# mask_value_pass = image_v > 128
_, mask_value_pass = cv.threshold(image_v, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
mask_value_pass = mask_value_pass.astype(bool)
mask_value_reject = ~mask_value_pass

# show_image(mask_value_reject.astype(np.uint8) * 255, "Value Reject Mask", downscale=3, stack=True)
# show_image(mask_value_pass.astype(np.uint8) * 255, "Value Pass Mask", downscale=3, stack=True)

mask_reject = mask_value_reject #| mask_sat_reject
mask_pass = mask_value_pass
background_mask = (~mask_reject | mask_pass)
# show_image(background_mask.astype(np.uint8) * 255, "Combined Background Mask", downscale=3, stack=True)

# run watershed on gradient of blurred image from above
# erode masks
mask_reject = cv.erode(mask_reject.astype(np.uint8), np.ones((5, 5), np.uint8), iterations=3).astype(bool)
mask_pass = cv.erode(mask_pass.astype(np.uint8), np.ones((5, 5), np.uint8), iterations=2).astype(bool)
markers = np.zeros(image.shape[:2], dtype=np.int32)
markers[mask_reject] = 2
markers[background_mask] = 1
show_image(markers.astype(np.uint8) * 127, "Markers", downscale=3, stack=True)

# sharpen gradients for image input
image = cv.filter2D(image, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
# make super gradients
image_blurred = cv.GaussianBlur(image, (11, 11), 0)
edges = cv.Canny(image, 100, 200)
# make edge points black on image
# image[edges == 255] = 25

cv.dilate(edges, np.ones((3, 3), np.uint8), iterations=1, dst=edges)
show_image(edges, "Canny Edges", downscale=3, stack=True)

markers = cv.watershed(image, markers)
markers = np.where(markers == 1, 255, 0).astype(np.uint8)  # background pixels set to 255, others to 0
# show_image(markers, "Watershed Result", downscale=3, stack=True)

# display watershed masks over original image using transparency
overlay = image.copy()
overlay[markers == 0] = [0, 0, 255]  # mark foreground regions in red
alpha = 0.5
cv.addWeighted(overlay, alpha, image, 1 - alpha, 0, overlay)
show_image(overlay, "Watershed Overlay", downscale=3, stack=True)




close_images_at_end()