'''
File for the top level window class and functions for the settings window for the algorithm
will be placed into menu bar under edit in future
'''

import cv2 as cv
import tkinter as tk
import pandas as pd
import tkinter.ttk as ttk

class AlgSettings :
    def __init__(self,defaultpath,normalpath):

        # JSON file path variables (default only read never edit)
        self.DefaultSettingsFilepath = defaultpath
        self.NormalSettingsFilepath = normalpath

        # Entry variables

        # frame variables
        self.root = tk.Tk()
        self.root.title('Algorithm Settings')
        self.root.geometry("400x800")
        # entry variables
       
        # button variables

    #reads settings file to local variables
    #def readSettings(self)
        

    # writes new entries into normal file
    #def writeSettings(self)
        

    # resets normal file to default settings
    #def resetSettings(self)
        