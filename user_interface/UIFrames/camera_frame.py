import tkinter as tk
import numpy as np
import cv2 as cv
from PIL import Image
from PIL import ImageTk
import subprocess
import os

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # full path to ffmpeg.exe
DEVICE_NAME = "UVC Camera"                 # exact name from Device Manager
WIDTH = 3840
HEIGHT = 2160
FPS = 30

class CameraFrame(tk.Frame):

    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        #TODO add script here (testing with my webcam rn)
        self.capture = cv.VideoCapture(0)

        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 800)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 800)

        self.canvas = tk.Canvas(self,width=800,height=800)
        self.canvas.grid(row=0,column=0)

        if not self.capture.isOpened():
            print("Cannot capture camera")
            exit() #not sure if this works how I want it to but fuck it
        else:
            #self.showCameraFrame() #starts showing camera here
            print("foundcamera")
        self.cameraToggle = True #true means camera is not on yet
        self.update()

    def showCameraFrame(self):
        ret, frame = self.capture.read()
        
        print("showing frame")
        #CV2 uses BGR, GUI needs to show RGB
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # convert to PIL image
            img = Image.fromarray(frame)
            #convert to imageTk image
            self.imgtk = ImageTk.PhotoImage(image=img)
            #configure new image to be displayed
            self.canvas.create_image(0,0,image=self.imgtk,anchor=tk.NW)
            self.canvas.update()
        #call this again to get frame TODO (will prob need to change number)
        self.after(100,self.showCameraFrame)