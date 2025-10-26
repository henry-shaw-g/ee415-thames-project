import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
'''
class MenuBar(tk.Menu):

    def __init__(self,parent,controller):
        self.Filemenu = tk.Menu(self.menubar,tearoff=0)
        self.Editmenu = tk.Menu(self.menubar,tearoff=0)
        self.Helpmenu = tk.Menu(self.menubar,tearoff=0)
        
        self.add_cascade(label="File",menu=self.Filemenu)
        self.add_cascade(label="Edit",menu=self.Editmenu)
        self.add_cascade(label="Help",menu=self.Helpmenu)

        #File menubar
        self.Filemenu.add_command(label="New Excel/CSV File",command=lambda: self.FileMB_new_file())
        self.Filemenu.add_command(label="Open Excel/CSV File",command=lambda: self.findExcelFile())
        self.Filemenu.add_separator()
        self.Filemenu.add_command(label="Save File",command=lambda: self.FileMB_save_file())
        self.Filemenu.add_command(label="Save File As",command=lambda: self.FileMB_save_file_as())
        self.Filemenu.add_separator()
        self.Filemenu.add_command(label="Find Image", command=lambda: self.getimg())
        self.Filemenu.add_separator
        self.Filemenu.add_command(label="Exit",command=lambda: self.FileMB_exit_program())

        #Edit menubar
        self.Editmenu.add_command(label="Edit Parameters",command=lambda: self.OpenAlgSettingsWindow())

        #Help menubar
        self.Helpmenu.add_command(label="FAQ")



    #alg settings window
    def OpenAlgSettingsWindow(self):
        #TODO code this
        pass
        
    def FileMB_new_file(self):
        pass

    def FileMB_save_file(self):
        pass

    def FileMB_save_file_as(self):
        pass

    def FileMB_exit_program(self):
        #TODO add popup confirmation
        self.root.destroy()

    def HelpMB_FAQ(self):
        pass

    def findExcelFile(self):
        self.ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if self.ExcelFilePath is None:
            print("Error: Did Not Save Filepath")
        else:
            print("Saved Filepath")

    def getimg(self):
        self.imgFilePath = filedialog.askopenfilename(title="Image to be Processed",filetypes=(("jpg","*.jpg"),("png","*.png")))
        print(self.imgFilePath)'''