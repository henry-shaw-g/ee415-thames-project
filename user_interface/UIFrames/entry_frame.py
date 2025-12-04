import tkinter as tk
import pandas as pd
import numpy as np
import os
from tkinter import messagebox

class EntryFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent, highlightbackground="green", highlightthickness=5)
        self.controller = controller

        #Data Inputs: TODO REWRITE FROM DATA FROM EXCEL FILE TO CUSTOMIZE (10-12 entries that show up based on number of excel file entries) (maybe loop creation of labels and entries?)
        #Need the following inputs:
        #Date Sampled, Date Processed (use time automatically?), Plot number, Hive ID, Trt number, Mite count, Bee count, mites per 100 bees (automatically do this calc), Initial, Notes, diet?
        self.LabelList = {}
        self.Labels = {} #create a list here for labels and entries, will create them based on the data obtained from the csv file
        self.Entries = {}
        self.numberOfLabels = 0 #will be filled as we add labels
        self.beeCountIndex = None #will be updated if we find while creating labels
        self.rowNum = None #gets filled in after we get filepath
        self.FilePath = None
        self.BeeCount = tk.IntVar()

    def updateFilePath(self,newPath):
        self.FilePath = newPath #updates excel filepath

    def getLabels(self):
        #configures label/entry widgets from csv file

        #first check if the excel filepath is valid
        if os.path.exists(self.FilePath) is not True:
            messagebox.showerror("Error", "Filepath is invalid")
            return False
        #then if it is valid we create the dataframe file to read the column names
        dataframefirst3 = pd.read_csv(self.FilePath, nrows=0, index_col=False) #only reads first 3 rows just to get column headers to save on processing time
        self.headers = list(dataframefirst3.columns)
        #then we save those to the list of labels and create label widgets for each with complimentary entries next to them, parsing for the bee count column
        checkVar = True
        indexVar = 0
        self.numberOfLabels = len(self.headers)
        isBeeCount = False
        while checkVar is True: #runs until we catalog each header
            if indexVar >= self.numberOfLabels:
                checkVar = False
            else: #could add more potential names for bee count here. will list in user manual
                if self.headers[indexVar] == "Bee Count" or self.headers[indexVar] == "Number of Bees" or self.headers[indexVar] == "bee count" or self.headers[indexVar] == "# of Bees":
                    isBeeCount = True
                self.createNewLabel(labelName=self.headers[indexVar],indexNum=indexVar,isBeeCount=isBeeCount)
                indexVar = indexVar + 1
                isBeeCount = False

        if self.beeCountIndex is None:
            messagebox.showerror("Error","No Bee Count Column Detected")
            return False
        
        return True #if all goes well we return true to keep going when setting up excel frame 

    def createNewLabel(self, labelName, indexNum, isBeeCount):
        self.LabelList[indexNum] = tk.StringVar()
        self.LabelList[indexNum].set(labelName)
        self.Labels[indexNum] = tk.Label(self,textvariable=self.LabelList[indexNum])
        self.Labels[indexNum].grid(row=indexNum,column=0,sticky='nsew')
        if isBeeCount is True:
            self.beeCountIndex = indexNum
            self.Entries[indexNum] = tk.Label(self, textvariable=self.BeeCount)
            self.Entries[indexNum].grid(row=indexNum,column=1,sticky='nsew')
        else:
            self.Entries[indexNum] = tk.Entry(self)
            self.Entries[indexNum].grid(row=indexNum,column = 1,sticky='nsew')
    
    def updateBeeCount(self,beeCount):
        self.BeeCount.set(f"{beeCount:d}")

    def saveDataToFile(self):
        pass

    def getDataFromRow(self,rowNum):
        #reads in data from file and updates entries based on given row
        self.rownum = rowNum #update value here
        dataframe = pd.read_csv(self.FilePath,nrows=1,skiprows=(rowNum - 1)) #skips rows until we get to the specified row and only reads that row
        #reads data from data frame into each entry