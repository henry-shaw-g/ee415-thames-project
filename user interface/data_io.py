import cv2 as cv
import tkinter as tk
from tkinter import filedialog
import pandas as pd


class DataIO:
    def __init__(self,csvfilepath):
        
        self.csvfilepath = None