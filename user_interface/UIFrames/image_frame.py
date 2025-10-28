import tkinter as tk
import tkinter.ttk as ttk
# from PIL import Image, ImageTk
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
import cv2 as cv


class ImageFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self._image_view_size = (800, 600)

        fig = Figure(figsize=(self._image_view_size[0]/100, self._image_view_size[1]/100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(np.zeros((1080, 1920), dtype=np.uint8))
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, pack_toolbar=False)
        toolbar.update()
        canvas.mpl_connect("key_press_event", key_press_handler)
        canvas.get_tk_widget().bind("<Configure>", lambda event: () )

        canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.NW, fill=tk.X)
        toolbar.pack(side=tk.TOP, fill=tk.X)

    def showImage(self,ImageFile):
        #function displays image in this frame (used for showing annotated bee image)
        #TODO connect w/ connor and henry about hooking this up on their end
        
        #also switches frames to image frame after image is shown to 
        self.controller.showFrame("ImageFrame")
        pass
