import wx
import wx.adv

#-----------------------------------------------------------
class WindowSelWorking (wx.Window):
    '''
    Window to select the working spreadsheet
    '''

    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self, *args, **kwargs)
        self.SetBackgroundColour("cornflower blue")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(20) # Inset content from top of window

        self.title = wx.StaticText(self, label="Spreadsheet Selection")
        self.title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.sizer.Add(self.title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 5)

        self.button = wx.Button(self, label="Select Working Spreadsheet")
        self.sizer.Add(self.button, 1, 5)

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.SetAutoLayout(1)

app = wx.App(False)

frame = wx.Frame(None, title="Bee/Mite Counter", size=(800, 600))

taskbar_icon = wx.adv.TaskBarIcon(iconType=wx.adv.TBI_DOCK)
taskbar_icon.SetIcon(wx.Icon("./gui_resources/bee_program_icon.bmp", wx.BITMAP_TYPE_BMP))
app.taskbar_icon = taskbar_icon

app_menu = wx.Menu()
app_menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
app_menu.Append(wx.ID_HELP, "&Help", "Help on this program")
app_menu.AppendSeparator()
app_menu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")

app_menu_bar = wx.MenuBar()
app_menu_bar.Append(app_menu, "&File")
frame.SetMenuBar(app_menu_bar)

sel_working_window = WindowSelWorking(frame)


frame.CreateStatusBar()

frame.Show(True)
app.MainLoop()

print("ending program")