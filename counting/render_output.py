'''
    Module for displaying detected bees, clumps, etc on images.
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt

def _is_contour_clump(contour):
    # awaiting contour implementation
    return contour.type == 'clump'

def _is_contour_single_bee(contour):
    # awaiting contour implementation
    return contour.type == 'single_bee'

'''
fn: _get_contour_ellipse
outputs: the center (x, y), size (w, h), and rotation angle (theta) of the ellipse fitting the contour
'''
def _get_contour_ellipse(contour):
    # awaiting contour implementation
    x, y, w, h, theta = contour.ellipse # destructure numpy array
    return (x, y), (w, h), theta

'''
fn: _get_contour_pts
outputs: the numpy array of contour points, provided by cv2.findContours
'''
def _get_contour_pts():
    pass

'''
fn: render_output
    Renders / annotates algorithm detection information onto copy of source image for display.
inputs:
    src_image: source image to render on (numpy array)
outputs:
    The rendered image, which is a copy of the source image with annotations drawn on it.
'''
def render_output(src_image, contours, settings):
    image = src_image.copy()

    single_bee_color = (0, 255, 0)
    clump_color = (255, 0, 0)
    unknown_color = (0, 0, 255)

    if settings is None: 
        settings = {}
    render_single_bee = settings.get("render_single_bee", True)
    render_single_bee_text = settings.get("render_single_bee_text", True)
    render_clump = settings.get("render_clump", True)
    render_clump_text = settings.get("render_clump_text", True)
    render_unknown = settings.get("render_unknown", True)
    render_unknown_text = settings.get("render_unknown_text", True)

    for contour in contours:
        (x, y), (w, h), theta = _get_contour_ellipse(contour)

        if _is_contour_single_bee(contour):
            if render_single_bee:
                # draw fitted ellipse of single bee
                cv2.ellipse(image, (int(x), int(y)), (int(w/2), int(h/2)), theta, 0, 360, single_bee_color, 2)
            if render_single_bee_text:
                bx, by, bw, bh = cv2.boundingRect(contour)
                cv2.putText(image, 
                            f"w:{bw:d},h:{bh:d},AR:{bh/bw:.2f}",
                            (bx, by-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, single_bee_color, 2)
        elif _is_contour_clump(contour):
            if render_clump:
                # draw contour outline of clumps
                pts = _get_contour_pts(contour)
                cv2.drawContours(image, [pts], -1, clump_color, 2)
            if render_clump_text:
                # draw clump area text
                bx, by, bw, bh = cv2.boundingRect(contour)
                cv2.putText(image, "C", (bx, by-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, clump_color, 2)
        else:
            if render_unknown:
                # draw unknown contour outline
                pts = _get_contour_pts(contour)
                cv2.drawContours(image, [pts], -1, unknown_color, 2)
            if render_unknown_text:
                # draw fitted ellipse text
                bx, by, bw, bh = cv2.boundingRect(contour)
                cv2.putText(image, 
                            f"w:{bw:d},h:{bh:d},AR:{bh/bw:.2f}",
                            (bx, by-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, unknown_color, 2)
                


if __name__ == "__main__":
    pass