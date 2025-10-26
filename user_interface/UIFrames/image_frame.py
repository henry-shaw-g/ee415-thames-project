import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np

class ImageFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="this is the Image Frame")
        label.pack(side="top", fill="x", pady=10)
        self._image_view_size = (800, 600)


        #TODO code in the image showing code w/ matplotlib
        
