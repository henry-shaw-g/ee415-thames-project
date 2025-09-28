import cv2 as cv
import tkinter as tk
from tkinter import filedialog
import pandas as pd


class DataIO:
    def __init__(self,csvfilepath):
        
        if csvfilepath is not None:
            self.csvFilePath = csvfilepath
        else:
            print("Error: No CSC file to write to")

        #variables for excel/csv file
        self.DateSample = None
        self.DateProcess = None
        self.HiveNum = None
        self.ShakerNum = None
        self.Initials = None
        self.Diet = None
        self.ACN = None
        self.Notes = None
        self.MiteNum = None
        self.bee_count = None

    def _record_results_to_excel(self):
        print("writing results to excel file {self.working_sheet_file_path}")
        # put excel file logic here
        if self.bee_count is not None:
            self.miteperbees = (float(self.MiteNum) / float(self.bee_count))*100 #calc for mite/100bees here
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

    def UpdateValues(self,mite_num,date_sample,date_process,hive_num,shaker_num,inits,diet,acn,notes,imgfilepath,csvfilepath,bee_count):
        self.bee_count = bee_count
        self.DateSample = date_sample
        self.DateProcess = date_process
        self.HiveNum = hive_num
        self.ShakerNum = shaker_num
        self.Initials = inits
        self.Diet = diet
        self.ACN = acn
        self.Notes = notes
        self.MiteNum = mite_num
        self.CSVFilePath = csvfilepath