import tkinter as tk
import cv2 as cv
from PIL import Image
from PIL import ImageTk

DEVICE_NAME = "UVC Camera"                 # exact name from Device Manager

class CameraFrame(tk.Frame):

    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        #TODO add script here (testing with my webcam rn)
        self.capture = cv.VideoCapture(DEVICE_NAME) #Get the correct camera
        if self.capture.isOpened() is not True:
            print("Error: Could not find correct camera. Using default camera")
            self.capture = cv.VideoCapture(0)  #If we can't find the correct device name then we just use the default

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

    def checkCamera(self):
        self.capture = cv.VideoCapture(DEVICE_NAME) #Try to get the correct camera again
        if self.capture.isOpened() is not True:
            print("Error: Could not find correct camera. Using default camera")
            self.capture = cv.VideoCapture(0)  #If we can't find the correct device name then we just use the default again

    def TakePhotoFromCamera(self):
        #assuming self.capture is not none so we just have access to it
        if self.imgtk is not None: #check to see if camera is running
            print("Taking photo")
            self.capturePhoto = cv.VideoCapture(DEVICE_NAME)
            if self.capturePhoto.isOpened(): # not sure if I need this but we run it
                #set new resolution for 4k picture
                self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 3840) #4k width
                self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 2160) #4k height
                
                width = self.capture.get(cv.CAP_PROP_FRAME_WIDTH)
                height = self.capture.get(cv.CAP_PROP_FRAME_HEIGHT)
                print(f"width: {width}, heigth: {height}") #check to make sure its printing the image at 4k

                ret,frame = self.capturePhoto.read() #actually get the photo
                if ret:
                    #reset capture size
                    self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 800)
                    self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 800) 

                    path = None #will save image and return its path 
                    return path #return image through function only if the capture worked
                else:
                    #reset capture size
                    self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 800)
                    self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 800) 
                    return None
            else:
                print("Error: Wrong Camera attatched, please attach correct camera")
                return None
        else:
            print("Error: No camera running")
            return None