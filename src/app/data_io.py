'''
Get image data, etc.

Exporting data to Excel. Creating new Excel files, Appending Data to existing Excel files
'''

import cv2 as cv
import tkinter as tk
from tkinter import filedialog
import pandas as pd


class DataIO:
    def __init__(self,mite_num,date_sample,date_process,hive_num,shaker_num,inits,diet,acn,notes,csvfilepath,imgfilepath,settingsfilepath):
        #data passed in from front end
        
        if csvfilepath is not None:
            self.CSVFilePath = csvfilepath
            self.ImgFilePath = imgfilepath
            self.SettingsFilePath = settingsfilepath
        else:
            print("Error: No CSC file to write to")
    
        self.DateSample = date_sample
        self.DateProcess = date_process
        self.HiveNum = hive_num
        self.ShakerNum = shaker_num
        self.Initials = inits
        self.Diet = diet
        self.ACN = acn
        self.Notes = notes
        self.MiteNum = mite_num
        self.bee_count = None

    '''
    Top level procedure to do all the required operations with the bee image
    '''
    def handle_image(self, *, sheet_file_path, use_camera: bool, img_path=None):
        self.working_sheet_file_path = sheet_file_path

        img: cv.typing.MatLike

        if use_camera:
            raise RuntimeError("Camera input not implemented yet.")
        else:
            imgpath = cv.imread(img_path)
            if img is None:
                raise RuntimeError("Image file cannot be read.")
            
            # here call counting
            self.results_img = None
            #should we round and have bee_count be an int or a float (proabably int)

            self._record_results_to_excel()
            self._display_results_to_gui()

    
    def _record_results_to_excel(self):
        print("writing results to excel file {self.working_sheet_file_path}")
        # put excel file logic here
        if self.bee_count is not None:
            self.miteperbees = (float(self.MiteNum) / float(self.bee_count))*100.0 #calc for mite/100bees here
            self.EntryData = pd.DataFrame(
                {
                    "Date: sample taken": self.DateSample,
                    "Date: sample processed": self.DateProcess,
                    "Shaker Number": self.ShakerNum,
                    "Hive ID": self.HiveNum,
                    "Mite Count": self.MiteNum,
                    "mites/100": self.miteperbees,
                    "Number of Bees": self.bee_count,
                    "Initial": self.Initials,
                    "DIET": self.Diet,
                    "APIX 1-2,COMP,NP": self.ACN,
                    "Column1": self.Notes
                }
                ,index=[0] #impliment indexing later, not now though
            )
            #append data to csv file (TO DO: work on creating a new file and work on being able to edit previous lines)
            self.EntryData.to_csv(self.CSVFilePath,mode='a',index=False,header=False)
            print("Data has been submitted")
        else:
            print("Error: No Bee Count Recorded")


#again, not sure we need this function, just call the static display using the img from mem (not even sure we need that tbh)
    def _display_results_to_gui():
        print("displaying results in GUI")
        # put logic to pass output images to GUI here (somehow)
        #no need for this, just pass new img to the static img function in front end display (maybe)
        pass