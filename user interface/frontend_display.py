'''
authors: Henry Shaw, John Pratt
date: 2025-09-28

notes:

'''
# library dependancies
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import time
# from PIL import Image, ImageTk
import cv2 as cv
import numpy as np
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
# files to import from
from data_io import DataIO
from alg_settings import AlgSettings




class FrontendDisplay:

    def __init__(self, counting_settings,default_counting_settings):
        #filepaths for both the normal and default counting setting JSON files
        self.counting_settings = counting_settings
        self.defualt_counting_settings = default_counting_settings

