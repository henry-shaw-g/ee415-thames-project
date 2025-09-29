'''
File for the top level window class and functions for the settings window for the algorithm
will be placed into menu bar under edit in future
'''

import cv2 as cv
import tkinter as tk
import pandas as pd
import tkinter.ttk as ttk

class AlgSettings :
    def __init__(self,defaultpath,normalpath,rootWindow):

        # JSON file path variables (default only read never edit)
        self.DefaultSettingsFilepath = defaultpath
        self.NormalSettingsFilepath = normalpath

        # data variables
        self.blur_ksize = [0,0]
        self.threshold_value = 0
        self.threshold_maxval = 0
        self.min_contour_area = 0
        self.max_contour_area = 0

        # frame variables
        self.Top = tk.Toplevel(rootWindow)
        self.Top.title('Algorithm Settings')
        self.Top.geometry("400x800")
        # entry variables

        # button variables


    #can expand overtime, not sure if it is needed
    def UpdateValues(self, newBlurKSize, newThresholdValue, newThresholdMaxVal, newMinContArea, newMaxContArea):
        self.blur_ksize = newBlurKSize
        self.threshold_value = newThresholdValue
        self.threshold_maxval = newThresholdMaxVal
        self.min_contour_area = newMinContArea
        self.max_contour_area = newMaxContArea

    #reads settings file to local variables
    def readSettings(self):

        if self.DefaultSettingsFilepath is None:
            print("Error: No default settings file found")
        else:
            print("Getting Algorithm Settings")


    def writeSettings(self):
        if self.DefaultSettingsFilepath and self.NormalSettingsFilepath is not None:
            print("Updating Settings")
        else:
            print("Error: No filepaths detected")