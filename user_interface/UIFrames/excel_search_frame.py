import tkinter as tk
import os
from tkinter import filedialog
from tkinter import messagebox

#not sure if I want this here or not (might be at bottom or inside of the control panel idk)
class ExcelSearchFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent, highlightbackground="blue", highlightthickness=5)
        self.controller = controller

        self.ExcelFilePath = None #storing this here for now, might move it over to a different class

        #TODO reformat these buttons sometime
        self.RowNumVar = tk.IntVar()
        self.PreviousEntryBtn = tk.Button(self,text="<<<",command=lambda: self.PreviousEntry())
        self.PreviousEntryBtn.grid(row=0,column=0,sticky='nsew')
        self.RowNumEntry = tk.Entry(self,textvariable=self.RowNumVar)
        self.RowNumEntry.grid(row=0,column=1,sticky='nsew')
        self.NextEntryBtn = tk.Button(self,text=">>>",command=lambda: self.NextEntry())
        self.NextEntryBtn.grid(row=0,column=2,sticky='nsew')
        self.FindFileBtn = tk.Button(self,text="Open CSV/Excel File", command=lambda: self.FileFind())
        self.FindFileBtn.grid(row=1,column=1,sticky='nsew')
        
        self.GoToRowBtn = tk.Button(self,text="Go To Row", command=lambda:self.GoToRow())
        self.GoToRowBtn.grid(row=2,column=1,sticky='nsew')
        pass
    
    def FileFind(self):
        ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if os.path.exists(ExcelFilePath):
            print("Saved Filepath")
            #if the filepath is not none and works, we update the filepath in the main frontend display file and show the data entry frame
            #This will be updated later to also get the labels for each column but for now is just a toggle and rigid categories
            #TODO do the above comment
            self.ExcelFilePath = ExcelFilePath
            self.controller.showFrame("EntryFrame")
            
        else:
           messagebox.showerror("Error", "Did Not Save Filepath")

    def updateFilePath(self,newFilePath):
        self.ExcelFilePath = newFilePath

    def PreviousEntry(self):
        pass

    def NextEntry(self):
        pass

    def GoToRow(self):
        rownum = self.RowNumEntry.get() #get row number to go to
        print(f"Going To Row: {rownum}")
        #call entry frame to update
        self.controller.frames["EntryFrame"].getDataFromRow(rownum)
        self.RowNumVar = rownum

    def findFirstEmptyRow(self):
        pass