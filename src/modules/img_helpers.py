import cv2 as cv

STD_FONT = cv.FONT_HERSHEY_SIMPLEX
STD_FONT_SCALE = 1

def ez_draw_text(img, text, pos, color=(255, 255, 255)):
    # TODO: add optional params for custom everything
    cv.putText(img, text, pos, STD_FONT, STD_FONT_SCALE, color, 2, cv.LINE_AA)