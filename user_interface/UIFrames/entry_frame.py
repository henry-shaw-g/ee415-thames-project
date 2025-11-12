import tkinter as tk
import tkinter.ttk as ttk
import time as time

class EntryFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent, highlightbackground="green", highlightthickness=5)
        self.controller = controller

        #Data Inputs: TODO REWRITE FROM DATA FROM EXCEL FILE TO CUSTOMIZE (10-12 entries that show up based on number of excel file entries) (maybe loop creation of labels and entries?)
        #Need the following inputs:
        #Date Sampled, Date Processed (use time automatically?), Plot number, Hive ID, Trt number, Mite count, Bee count, mites per 100 bees (automatically do this calc), Initial, Notes, diet?
        
        self.Labels = {} #create a list here, will create them based on the data obtained from the csv file
        
        
        #Old Data inputs
        #Bee Count
        self.BeeCount = tk.IntVar()
        self.lbl1BeeCount = ttk.Label(self, text = "Bee Count: ").grid(row=9,column=1,sticky="W")
        self.lblBeeCount = ttk.Label(self, textvariable=self.BeeCount)
        self.lblBeeCount.grid(row=9,column=2,sticky="W")

        #Date Sampled
        self.lblDateSample = tk.Label(self,text="Date Sampled: ").grid(row=0,column=1,sticky="W")
        self.entDateSample = tk.Entry(self)
        self.entDateSample.grid(row=0,column=2)
        #Date Processed 
        self.lblDateProcess = tk.Label(self,text="Date Processed: ").grid(row=1,column=1,sticky="W")
        self.entDateProcess = tk.Label(self,text=time.strftime("%D",time.localtime()))
        self.entDateProcess.grid(row=1,column=2,sticky="W")
        #Hive number
        self.lblHiveNum = tk.Label(self,text="Hive Number: ").grid(row=2,column=1,sticky="W")
        self.entHiveNum = tk.Entry(self)
        self.entHiveNum.grid(row=2,column=2)
        #Shaker number
        self.lblShakerNum = tk.Label(self,text="Shaker Number: ").grid(row=3,column=1,sticky="W")
        self.entShakerNum = tk.Entry(self)
        self.entShakerNum.grid(row=3,column=2)
        #Mite Count
        self.MiteNum = tk.Label(self,text="Number of Mites: ").grid(row=4,column=1,sticky="W")
        self.entMiteNum = tk.Entry(self)
        self.entMiteNum.grid(row=4,column=2)
        #Initials
        self.lblInits = tk.Label(self,text="Initials: ").grid(row=5,column=1,sticky="W")
        self.entInits = tk.Entry(self)
        self.entInits.grid(row=5,column=2)
        #Diet
        self.lblDiet = tk.Label(self,text="Diet: ").grid(row=6,column=1,sticky="W")
        self.entDiet = tk.Entry(self)
        self.entDiet.grid(row=6,column=2)
        #APIX 1-2, COMP,NF (Make radio buttons later? or drop down menu?)
        self.lblACN = tk.Label(self,text="APIX 1/2, COMP or NF: ").grid(row=7,column=1,sticky="W")
        self.entACN = tk.Entry(self)
        self.entACN.grid(row=7,column=2)
        #notes
        self.lblnotes = tk.Label(self,text="Additional Notes: ").grid(row=8,column=1,sticky="W")
        self.entnotes = tk.Entry(self)
        self.entnotes.grid(row=8,column=2)

    def getLabels(self):
        #
        pass

    def createNewLabels(self):
        #will be part of the file creation in the UI process (called after entering however many categories they want to track)
        pass

    def updateLabels(self):
        pass
    
    def updateBeeCount(self,beeCount):
        self.BeeCount.set(f"{beeCount:d}")
        pass