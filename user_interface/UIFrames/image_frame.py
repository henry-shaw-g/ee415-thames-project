import tkinter as tk
import tkinter.ttk as ttk
# from PIL import Image, ImageTk
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
import cv2 as cv
from PIL import ImageTk


class ImageFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self._image_view_size = (self.controller.windowWidth*0.8, self.controller.windowHeight*0.8)

        self.fig = Figure(figsize=(self._image_view_size[0]/100, self._image_view_size[1]/100), dpi=100)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.imshow(np.zeros((1080, 1920), dtype=np.uint8))
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, pack_toolbar=False)
        self.toolbar.update()
        self.canvas.mpl_connect("key_press_event", key_press_handler)
        self.canvas.get_tk_widget().bind("<Configure>", lambda event: () )

        self.canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.NW, fill=tk.X)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def showImage(self,ImageFile):
        #function displays image in this frame (used for showing annotated bee image)
        #TODO connect w/ connor and henry about hooking this up on their end
        OpenedImage = cv.imread(ImageFile)
        img = ImageTk.PhotoImage(OpenedImage)

        matplot_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.ax.clear()
        self.ax.imshow(matplot_img)

        self.canvas.draw_idle()
        self.toolbar.update()
        self.update()
        
        #also switches frames to image frame after image is shown to 
        self.controller.showFrame("ImageFrame")

    def show_image_from_data(self, image_data):
        matplot_img = cv.cvtColor(image_data, cv.COLOR_BGR2RGB)
        self.ax.clear()
        self.ax.imshow(matplot_img)

        self.canvas.draw_idle()
        self.toolbar.update()
        self.update()
        
        #also switches frames to image frame after image is shown to 
        self.controller.showFrame("ImageFrame")