'''
Get image data, etc.

Exporting data to Excel. Creating new Excel files, Appending Data to existing Excel files
'''

import cv2 as cv
import tkinter as tk
from tkinter import filedialog
import pandas as pd


class DataIO:
    def __init__(self):
        self.BeeCount = 0.0
        pass
    
    BeeNumber = 0.0
    MiteNumber = 0
    DateSampled = None
    DateProcess = None
    HiveNum = None
    ShakerNum = None
    Initials = None
    Diet = None
    MiteRatio = 0.0
    ACN = None
    Notes = None

    '''
    Top level procedure to do all the required operations with the bee image
    '''
    def handle_image(self, *, sheet_file_path, use_camera: bool, img_path=None):
        self.working_sheet_file_path = sheet_file_path

        img: cv.typing.MatLike

        if use_camera:
            raise RuntimeError("Camera input not implemented yet.")
        else:
            imgpath = cv.imread(img_path)
            if img is None:
                raise RuntimeError("Image file cannot be read.")
            
            # here call counting
            self.results_img = None
            self.BeeCount.set(350)

            self._record_results_to_excel()
            self._display_results_to_gui()

    
    def _record_results_to_excel(self, SheetFilePath=None,SampleDate=None,ProcessDate=None,HiveNum=None,ShakerNum=None,):
        print("writing results to excel file {self.working_sheet_file_path}")
        # put excel file logic here

        pass

    def _display_results_to_gui():
        print("displaying results in GUI")
        # put logic to pass output images to GUI here (somehow)
        #no need for this, just pass new img to the static img function in front end display (maybe)
        pass