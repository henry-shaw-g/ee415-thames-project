'''
Experiment to learn how to edge detect using OpenCV.
Results might also give indication of clumped bees being detectable.
'''

import sys
sys.path.append('..')
from modules import imgprocx

import numpy as np
import cv2 as cv

img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)
img = img[500:1500, 500:1500]

KERNEL_SIZE = 5
BLUR_SIZE = 5
THRESHOLD1 = 70
THRESHOLD2 = 120


# cv.imshow('Edges', edges)

# cv.imwrite('outputs/bee-image1-edgepass.png', img_out)

# wait for key press
# cv.waitKey(0)
# cv.destroyAllWindows()

v = 0

class SessionDispatch:
    def process(self, _):
        print("Processing.")
        global THRESHOLD2
        THRESHOLD2 = self.session.check_slider_input("Threshold2")
        global THRESHOLD1
        THRESHOLD1 = self.session.check_slider_input("Threshold1")
        print(f"{THRESHOLD1=}, {THRESHOLD2=}")

        # do gradient magnitude (edge detection)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (7, 7), 0)

        edges = cv.Canny(gray, THRESHOLD1, THRESHOLD2)
        ret, mask = cv.threshold(edges, 100, 255, cv.THRESH_BINARY)
        edges_rgb = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
        edges_rgb = edges_rgb * np.array([1, 0, 1], dtype=np.uint8)
        mask_inv = cv.bitwise_not(edges)

        img_out = cv.bitwise_and(img, img, mask=mask_inv)
        img_out = cv.add(img_out, edges_rgb)

        self.session.push_img(edges_rgb)

sess = imgprocx.Session(title="Edge Detection", session_dispatch=SessionDispatch())
sess.reg_slider_input("Threshold1", "Threshold1", 0, 255, 70, 1)
sess.reg_slider_input("Threshold2", "Threshold2", 0, 255, 120, 2)
sess.reg_slider_input("Threshold2", "Threshold2", 0, 255, 120, 2)
sess.run()