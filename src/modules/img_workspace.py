'''
author: Henry Shaw
version: 0.2
date: 20250227

Utility for testing image processing algorithsm by
displaying the image along with tuninig controls and 
controls to reprocess the output result.
'''

import wx
import wx.adv
import cv2 as cv

class WorkspaceEventHandler:
    '''
    Do processing for test session here.
    '''
    def __init__(self, *args, **kwargs):
        self.workspace = None
        pass

    def process(self, _):
        '''
        Should get new user spec. params and recompute image output.
        '''
        pass

class Workspace:
    def __init__(self, title="Image Workspace", event_handler=None, layout="vertical"):
        self.handler = event_handler
        if self.handler is not None:
            self.handler.workspace = self

        self.app = wx.App()
        self.frame = wx.Frame(None, title=title, size=(800, 600))
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.img_panel = wx.StaticBitmap(self.frame)
        self.top_sizer.Add(self.img_panel, 1, wx.EXPAND)

        

        self.input_panel = wx.Panel(self.frame)
        self.input_panel.SetMinSize((200, 200))
        self.top_sizer.Add(self.input_panel, 0, wx.EXPAND)
        self.input_box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_panel.SetSizer(self.input_box_sizer)
        
        self.process_btn = wx.Button(self.input_panel, label="Recompute")
        self.input_box_sizer.Add(self.process_btn, 0, wx.CENTER)
        self.process_btn.Bind(wx.EVT_BUTTON, self.handler.process)

        self.input_ctrls = {}

        self.frame.SetSizer(self.top_sizer)

    def run(self):
        self.frame.Layout()
        self.frame.Update()
        self.frame.Show()

        self.app.MainLoop()

    class SliderInput:
        sizer: wx.BoxSizer
        nameText: wx.StaticText
        slider: wx.Slider

    class RangeInput:
        sizer: wx.BoxSizer
        nameText: wx.StaticText
        minCtrl: wx.TextCtrl
        maxCtrl: wx.TextCtrl
        range: tuple[int, int]
        

    def reg_slider_input(self, id, name, min, max, value, order=None):
        order = order or 999999999
        slider_input = self.SliderInput()
        slider_input.sizer = wx.BoxSizer(wx.HORIZONTAL)
        slider_input.nameText = wx.StaticText(self.input_panel, label=name)
        slider_input.sizer.Add(slider_input.nameText, 1)
        slider_input.slider = wx.Slider(self.input_panel, value=value, minValue=min, maxValue=max, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        slider_input.sizer.Add(slider_input.slider, 3)
        self.input_box_sizer.Add(slider_input.sizer, 0, wx.CENTER)
        self.input_ctrls[id] = slider_input
        pass

    def check_slider_input(self, id):
        '''
        Slider id must have been previously registered.
        '''
        slider = self.input_ctrls.get(id)
        if slider is None: raise RuntimeError(f"Slider with id {id} not found.")
        return slider.slider.GetValue()

    def reg_range_input(self, id, name, range, value, order=None):
        # so wx-python doesn't actually have double ended slider so will just use 2 number inputs
        range_input = self.RangeInput()
        range_input.range = range
        range_input.sizer = wx.BoxSizer(wx.HORIZONTAL)
        range_input.nameText = wx.StaticText(self.input_panel, label=name)
        range_input.sizer.Add(range_input.nameText, 1)
        range_input.minCtrl = wx.TextCtrl(self.input_panel, value=str(value[0]), style = wx.TE_DONTWRAP | wx.TE_CENTER)
        range_input.sizer.Add(range_input.minCtrl, 1)
        range_input.maxCtrl = wx.TextCtrl(self.input_panel, value=str(value[1]), style = wx.TE_DONTWRAP | wx.TE_CENTER)
        range_input.sizer.Add(range_input.maxCtrl, 1)
        self.input_box_sizer.Add(range_input.sizer, 0, wx.CENTER)
        self.input_ctrls[id] = range_input
        pass

    def check_range_input(self, id) -> tuple[int, int]:
        # dont feel like doing event handling on the side so for now,
        # just try to parse text inputs, then fall back to the range values

        range_input = self.input_ctrls.get(id)
        if range_input is None: raise RuntimeError(f"RangeInput with id {id} not found.")

        low: float
        try:
            low = float(range_input.minCtrl.GetValue())
        except ValueError:
            low = range_input.range[0]
        
        high: float
        try:
            high = float(range_input.maxCtrl.GetValue())
        except ValueError:
            high = range_input.range[1]

        return (low, high)

    def reg_num_input(self, id, value, order=None):
        order = order or 999999999
        pass

    def check_num_input(self, id):
        '''
        Number input id must have been previously registered.
        '''
        pass

    def reg_bool_input(self, id, value: bool, order=None):
        # not implemented
        pass

    def check_bool_input(self, id) -> bool:
        # not implemented
        pass

    def push_img(self, img_mat):
        # todo: enforce correct ndarray and element type of img_mat
        bmp = wx.Bitmap.FromBuffer(img_mat.shape[1], img_mat.shape[0], img_mat)
        self.img_panel.SetBitmap(bmp)
        self.frame.Layout()
        self.frame.Update()

    def push_img_bgr(self, img_mat):
        img_mat = cv.cvtColor(img_mat, cv.COLOR_BGR2RGB)
        self.push_img(img_mat)

    def push_img_gray(self, img_mat):
        img_mat = cv.cvtColor(img_mat, cv.COLOR_GRAY2RGB)
        self.push_img(img_mat)

    def show_img(self):
        # load image in open cv and then use the mat data to show the image in self.img_panel
        img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_RGB)
        bmp = wx.Bitmap.FromBuffer(img.shape[1], img.shape[0], img)
        self.img_panel.SetBitmap(bmp)
        self.frame.Layout()
        self.frame.Update()

'''
if __name__ == "__main__":
    class TestDispatch:
        def process(self, _):
            print("Processing.")
            t1 = self.session.check_slider_input("Threshold1")
            print(t1)

    sess = Session(title="imgprocx test", session_dispatch=TestDispatch())
    sess.reg_slider_input("Threshold1", "Threshold1", 0, 255, 70, 1)
    sess.show_img()
    sess.run()
    # sess.app.MainLoop()'
'''