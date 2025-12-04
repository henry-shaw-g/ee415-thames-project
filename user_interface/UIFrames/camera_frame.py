import tkinter as tk
import cv2 as cv
from PIL import Image
from PIL import ImageTk
from tkinter import messagebox

#DEVICE_NAME = "UVC Camera"                 # exact name from Device Manager

class CameraFrame(tk.Frame):

    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.no_live_read = False #what is this for?

        self.cameraIndexNum = 0
        self.capture = cv.VideoCapture(self.cameraIndexNum, cv.CAP_DSHOW) #Get the correct camera
        if self.capture.isOpened() is not True:
            print("Error: Could not find correct camera. Using default camera")
            self.capture = cv.VideoCapture(0)  #If we can't find the correct device name then we just use the default

        #sets the size of the capture of the video, not the canvas
        self.set_capture_size_photo()

        #sets the size of the canvas, not the stream
        self.wide = self.controller.windowWidth * 0.8
        self.high = self.controller.windowHeight * 0.8
        print(f"width:{self.wide},height:{self.high}")
        self.canvas = tk.Canvas(self,width=self.wide,height=self.high)
        self.canvas.grid(row=0,column=0)

        self.cameraToggle = True #true means camera is not on yet
        self.update()
        self.showCameraFrame()

    def showCameraFrame(self):
        ret, frame = self.capture.read()

        if ret:
            #resize frame to only be 1280 x 720
            frame = cv.resize(frame, (1280,720))
            #CV2 uses BGR, GUI needs to show RGB
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # convert to PIL image
            img = Image.fromarray(frame)
            #convert to imageTk image
            self.imgtk = ImageTk.PhotoImage(image=img)
            #configure new image to be displayed
            self.canvas.create_image(0, 0,image=self.imgtk,anchor=tk.NW)
            self.canvas.update()
        #call this again to get frame TODO (will prob need to change number)
        self.after(100, self.showCameraFrame)

    def checkCamera(self):
        self.capture = cv.VideoCapture(self.cameraIndexNum) #Try to get the correct camera again
        if self.capture.isOpened() is not True:
            print("Error: Could not find correct camera. Using default camera")
            self.capture = cv.VideoCapture(0)  #If we can't find the correct device name then we just use the default again

    def TakePhotoFromCamera(self):
        #assuming self.capture is not none so we just have access to it
        print("Taking photo")
        if self.capture.isOpened(): # not sure if I need this but we run it
                
            #set to 4k image here
            #self.set_capture_size_photo()

            #4k check
            width = self.capture.get(cv.CAP_PROP_FRAME_WIDTH)
            height = self.capture.get(cv.CAP_PROP_FRAME_HEIGHT)
            print(f"width: {width}, heigth: {height}") 
            ret,frame = self.capture.read() #actually get the photo

            #reset capture size back to live here after we get photo
            #self.set_capture_size_live()

            if ret: #return image through function only if the capture worked
                return frame
            else:
                messagebox.showerror("Error","No Frame Available")
                return None
        else:
            print("Error: Wrong Camera attatched, please attach correct camera")
            messagebox.showerror("Error","Camera not opened, please ensure camera is connected")
            return None
        
    def detectCamera(self):
        #essentially toggles through cameras until we either get a new camera or loop around back to the default (0)
        self.cameraIndexNum = self.cameraIndexNum + 1
        self.capTest = cv.VideoCapture(self.cameraIndexNum, cv.CAP_DSHOW)
        if self.capTest.isOpened():
            self.capture = self.capTest #If the test camera works and is open, then that is the new video stream to pull from
        else: #if its not open (aka cam doesnt exist)
            self.cameraIndexNum = 0 #set to default
            self.capture = cv.VideoCapture(self.cameraIndexNum, cv.CAP_DSHOW) #show default cam

    def set_capture_size_live(self):
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    def set_capture_size_photo(self):
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 3840) #4k width
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 2160) #4k height
