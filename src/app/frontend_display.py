'''
authors: Henry Shaw
date: 2025-04-05

notes:
This module is for the demo. This will handle non-interactive gui of algorithm
output. TUI and worker logic should interface with this.
To use, the entry point needs to start the frontend object and pass its 
worker / TUI code, which will be ran in a separate thread. The frontend will then be able to call the TUI methods to update the display.
'''

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

import queue
from queue import Queue

from .data_io import DataIO
from .counting import Counting

QUEUE_CHECK_PERIOD = 100 # ms

class FrontendDisplay:

    def __init__(self, counting_settings):
        self.counting_settings = counting_settings

        self._image_view_size = (800, 600)

        # create Tk gui instances
        self.root = tk.Tk()
        self.root.title("Bee Count Display")
        self.root.geometry(f"{self._image_view_size[0]}x{self._image_view_size[1]}")

        self.style = ttk.Style(self.root)
        self.style.theme_use("classic")

        self.top_frame = ttk.Frame(self.root)
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # starting frame which shows black background and pending input text:
        self.empty_frame = ttk.Frame(self.top_frame)
        self.empty_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.empty_label = ttk.Label(self.empty_frame, text="Awaiting input...")
        self.empty_label.pack(anchor=tk.CENTER, side=tk.TOP, fill=tk.Y, expand=True)
        # create a canvas to display images

        self.result_frame = ttk.Frame(self.top_frame)
        self.result_frame.grid(row=0, column=0, sticky="nsew")
        self.result_frame.grid_rowconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=3)
        self.result_frame.grid_columnconfigure(1, weight=1)

        self.result_frame_left = ttk.Frame(self.result_frame)
        self.result_frame_left.grid(row=0, column=0, sticky="nsew")
        self.result_frame_right = ttk.Frame(self.result_frame)
        self.result_frame_right.grid(row=0, column=1, sticky="nsew")
        
        # create a matlab figure canvas for image display, hook up input events for navigation
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
        # self.result_ax_im = ax_im

        self.result_frame.tkraise()

        #Data Inputs:
        #Bee Count
        self.BeeCount = tk.IntVar()
        self.lbl1BeeCount = ttk.Label(self.result_frame_right, text = "Bee Count: ").grid(row=9,column=1,sticky="W")
        self.lblBeeCount = ttk.Label(self.result_frame_right, textvariable=self.BeeCount)
        self.lblBeeCount.grid(row=9,column=2,sticky="W")

        #Date Sampled
        self.lblDateSample = tk.Label(self.result_frame_right,text="Date Sampled: ").grid(row=0,column=1,sticky="W")
        self.entDateSample = tk.Entry(self.result_frame_right)
        self.entDateSample.grid(row=0,column=2)
        #Date Processed 
        self.lblDateProcess = tk.Label(self.result_frame_right,text="Date Processed: ").grid(row=1,column=1,sticky="W")
        self.entDateProcess = tk.Label(self.result_frame_right,text=time.strftime("%D",time.localtime()))
        self.entDateProcess.grid(row=1,column=2,sticky="W")
        #Hive number
        self.lblHiveNum = tk.Label(self.result_frame_right,text="Hive Number: ").grid(row=2,column=1,sticky="W")
        self.entHiveNum = tk.Entry(self.result_frame_right)
        self.entHiveNum.grid(row=2,column=2)
        #Shaker number
        self.lblShakerNum = tk.Label(self.result_frame_right,text="Shaker Number: ").grid(row=3,column=1,sticky="W")
        self.entShakerNum = tk.Entry(self.result_frame_right)
        self.entShakerNum.grid(row=3,column=2)
        #Mite Count
        self.MiteNum = tk.Label(self.result_frame_right,text="Number of Mites: ").grid(row=4,column=1,sticky="W")
        self.entMiteNum = tk.Entry(self.result_frame_right)
        self.entMiteNum.grid(row=4,column=2)
        #Initials
        self.lblInits = tk.Label(self.result_frame_right,text="Initials: ").grid(row=5,column=1,sticky="W")
        self.entInits = tk.Entry(self.result_frame_right)
        self.entInits.grid(row=5,column=2)
        #Diet
        self.lblDiet = tk.Label(self.result_frame_right,text="Diet: ").grid(row=6,column=1,sticky="W")
        self.entDiet = tk.Entry(self.result_frame_right)
        self.entDiet.grid(row=6,column=2)
        #APIX 1-2, COMP,NF (Make radio buttons later? or drop down menu?)
        self.lblACN = tk.Label(self.result_frame_right,text="APIX 1/2, COMP or NF: ").grid(row=7,column=1,sticky="W")
        self.entACN = tk.Entry(self.result_frame_right)
        self.entACN.grid(row=7,column=2)
        #notes
        self.lblnotes = tk.Label(self.result_frame_right,text="Additional Notes: ").grid(row=8,column=1,sticky="W")
        self.entnotes = tk.Entry(self.result_frame_right)
        self.entnotes.grid(row=8,column=2)

        #File Paths
        self.imgFilePath = tk.StringVar()
        self.SettingsFilePath = tk.StringVar()
        self.OpenedImage = None
        self.ExcelFilePath = None
        self.BeeData = None
        #self.ifCSV = bool #want to add .xlsx handling later

        tk.Button(self.result_frame_right,text="Find Photo",command=self.getimg).grid(row=0,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Process Photo",command=self.processimg).grid(row=1,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Submit",command=self.submit).grid(row=2,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Settings",command=self.editparam).grid(row=3,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Exit",command=self.root.destroy).grid(row=4,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Find CSV",command=self.findExcelFile).grid(row=5,column=0,sticky="W")

    def submit(self):
        if self.BeeCount is not None: #only run once we get a count for bees
            #Variable Pass in Order: mite_num,date_sample,date_process,hive_num,shaker_num,inits,diet,acn,notes,imgfilepath,csvfilepath
            self.BeeData.UpdateValues(self.entMiteNum.get(),self.entDateSample.get(),self.entDateProcess.cget("text"),self.entHiveNum.get(),self.entShakerNum.get(),self.entInits.get(),
                                    self.entDiet.get(),self.entACN.get(),self.entnotes.get(),self.imgFilePath,self.ExcelFilePath,self.BeeCount.get())
            #update values above to BeeData DataIO object
            print("submitting data")
            self.BeeData._record_results_to_excel()
        else:
            print("Error: Image has not been processed, Bee Count is still 0")

    #Function of "settings" button that updates algorithm settings based on provided text file
    def editparam(self):
        print("editing parameters")
        self.SettingsFilePath = filedialog.askopenfilename(title="Text file for changing values",filetypes=(("text files","*.txt"),("all file types","*.*")))
        print(self.SettingsFilePath)


    #Function of "get photo button". Returns an image filepath, opened image object and displays said image
    def getimg(self):
        self.imgFilePath = filedialog.askopenfilename(title="Image to be Processed",filetypes=(("jpg","*.jpg"),("png","*.png")))
        print(self.imgFilePath)
        self.OpenedImage = cv.imread(self.imgFilePath)
        # self._on_static_result(self.OpenedImage)
        self.show_img_in_viewer(self.OpenedImage)

    #Function of "process photo" button. Starts algorithm to process image
    # use either image opened image
    #returns self.BeeCount
    def processimg(self):
        # TODO: maybe re-structure this ...
       # if self.OpenedImage != None: #makes sure that image has been opened before running alg.
        print("processing image")
        if self.BeeData is None:
            self.BeeData = DataIO(self.ExcelFilePath,self.imgFilePath,self.SettingsFilePath)
        else:
            self.BeeData.UpdatePaths(self.ExcelFilePath,self.SettingsFilePath,self.imgFilePath)
        #image processing alg here
        counting = Counting(self.OpenedImage, self.counting_settings)
        self.counting_settings.refresh()
        num = counting.count()
        counting.draw_results_all()
        self.counting_settings.refresh()    # force settings file to read any defaults

        #put call for image processing here (bee count )
        self.BeeCount.set(num) # self.BeeData.returnBeeCount()
        #image processing alg here (bee count number here for now, update later)
        
        self.show_img_in_viewer(counting.img_draw)

    #Function returns excel file
    def findExcelFile(self):
        self.ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if self.ExcelFilePath is None:
            print("Error: Did Not Save Filepath")
        else:
            print("Saved Filepath")

    def start(self):
        self.root.mainloop()


    def show_img_in_viewer(self, img: cv.typing.MatLike):
        matplot_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        # self.result_ax_im.set_data(matplot_img)
        # # self.result_ax.clear()
        # # self.result_ax.axis("off")
        # self.result_ax.imshow(matplot_img)
        self.result_ax.clear()
        self.result_ax.imshow(matplot_img)

        self.result_canvas.draw_idle()
        self.result_toolbar.update()
        self.result_frame.update()
        self.result_frame.tkraise()

