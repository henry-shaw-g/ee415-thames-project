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
        label = tk.Label(self, text="this is the Image Frame")
        label.pack(side="top", fill="x", pady=10)
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

        #TODO code in the image showing code w/ matplotlib

        ''' # create a matlab figure canvas for image display, hook up input events for navigation
        fig = Figure(figsize=(self._image_view_size[0] / 100, self._image_view_size[1] / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        # ax_im = ax.imshow(np.zeros((1080, 1920, 3), dtype=np.uint8))
        # ax.axis("off")
        ax.imshow(np.zeros((1080, 1920), dtype=np.uint8))
        ax.axis("off")

        # ax.imshow(np.zeros((1, 1, 3), dtype=np.uint8))
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame_left)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self.result_frame_left, pack_toolbar=False)
        toolbar.update()
        canvas.mpl_connect("key_press_event", key_press_handler)
        canvas.get_tk_widget().bind("<Configure>", lambda event: () )

        canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.NW, fill=tk.X)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.result_canvas = canvas
        self.result_toolbar = toolbar
        self.result_fig = fig
        self.result_ax = ax
        # self.result_ax_im = ax_im'''