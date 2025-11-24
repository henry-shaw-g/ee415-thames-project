'''
module:     frontend_state
    This implements the state machine for the frontend and handles locking data and user inputs for specific stages.
'''

import os

from enum import Enum
import cv2 as cv

REQUIRE_RESET_CONFIRM = False
USE_DUMMY_INPUT_IMAGE = False
DUMMY_INPUT_IMAGE_ENV_VAR = "BEE_DUMMY_INPUT"

class FrontendState:
    class State(Enum):
        LOADING = 1 # might not be used
        IMAGE_PENDING = 2 # user needs to load from file or camera
        IMAGE_LOADED = 3 # image is loaded and ready for processing
        IMAGE_PROCESSING_READY = 3.5 # user has accepted loaded image and is ready to process (OPTIONAL, might not be used in interface)
        IMAGE_PROCESSING = 4 # image is being processed
        SHOWING_RESULTS = 5 # results are being displayed to user
        SAVED_RESULTS = 6 # results have been saved, safe to go back to image_pending or image_loaded

    class OutputCommand(Enum):
        HALT = 0 # do not proceed to next action
        PROCEED = 1 # can go to next action as requested
        RESET_CONFIRM = 2 # issue a confirmation popup for resetting

    def _transition(self, new_state):
        self.state = new_state
        self.reset_confirm = False
        self.halt_reason = None

    def __init__(self, *, counting_module, default_counting_settings):
        self.state = self.State.IMAGE_PENDING
        self.lock = False
        self.loaded_image = None
        self.algorithm_output = None
        self.reset_confirm = False
        self.halt_reason = None

        self.counting_module = counting_module
        self.default_counting_settings = default_counting_settings

    '''
    fn: load_image
        Call when user requests to load an image from file or camera.
        Can only be called when in IMAGE_PENDING state.
        If successful, it transitions to IMAGE_LOADED state.
    input:
        path: Optional; file path to load image from.
        image_data: Optional; image data provided directly.
    '''
    def load_image(self, *, path=None, image_data=None):
        # halt if state is not IMAGE_PENDING
        if self.state != self.State.IMAGE_PENDING:
            return self.OutputCommand.HALT
        
        if path is not None:
            self.lock = True
            loaded_image =cv.imread(path)
            self.lock = False

            if loaded_image is None:
                self.halt_reason = f"Failed to load image from path: {path}"
                return self.OutputCommand.HALT
            
            self.loaded_image = loaded_image
        elif image_data is not None:
            self.loaded_image = image_data
        else:
            self.halt_reason = "No image parameter provided by code."
            return self.OutputCommand.HALT

        self._transition(self.State.IMAGE_LOADED)
        return self.OutputCommand.PROCEED       

    '''
    fn: ready_process_image
        Call when user indicates they are ready to process the loaded image.
        Can only be called when in IMAGE_LOADED state.
        If successful, it transitions to IMAGE_PROCESSING_READY state.
        If you want to bypass this, call this then immediately call process_image().
    '''
    def ready_process_image(self):
        if self.state == self.State.IMAGE_LOADED:
            self._transition(self.State.IMAGE_PROCESSING_READY)
            return self.OutputCommand.PROCEED
        else:
            return self.OutputCommand.HALT
    
    '''
    fn: process_image
        Call when user requests to process the loaded image.
        Can only be called when in IMAGE_PROCESSING_READY state.
        If successful, it transitions to IMAGE_PROCESSING state.
        Note that currently the algorithm runs synchronously here.
    outputs:
        output command: PROCEED if processing started, HALT otherwise.
            If HALT is returned call get_halt_reason() for a description.
    '''
    def process_image(self):
        if USE_DUMMY_INPUT_IMAGE:
            dummy_image_path = os.getenv(DUMMY_INPUT_IMAGE_ENV_VAR, None)
            if dummy_image_path is not None and os.path.isfile(dummy_image_path):
                self.loaded_image = cv.imread(dummy_image_path)
            else:
                self.halt_reason = f"Dummy input image path invalid or not set: {dummy_image_path}"
                return self.OutputCommand.HALT

            self.loaded_image = cv.imread(dummy_image_path)
            if self.loaded_image is None:
                self.halt_reason = f"Failed to load dummy image from path: {dummy_image_path}"
                return self.OutputCommand.HALT

        if self.state == self.State.IMAGE_PROCESSING_READY and not self.lock:
            self._transition(self.State.IMAGE_PROCESSING)
            self.lock = True
            # perform image processing here
            # self.loaded_image should be set before calling this
            self.algorithm_output = self.counting_module.algorithm(image_data=self.loaded_image, settings_path=None)
            self.lock = False
            return self.OutputCommand.PROCEED
        else:
            return self.OutputCommand.HALT

    '''
    fn: save_results
        Just intermediate state to separate processing and showing results.
    '''
    def show_results(self):
        if self.state == self.State.IMAGE_PROCESSING and not self.lock:
            self._transition(self.State.SHOWING_RESULTS)
            return self.OutputCommand.PROCEED
        else:
            return self.OutputCommand.HALT

    '''
    fn: reset
        Call when user requests to reset to IMAGE_PENDING state.
        Can be called when in SAVED_RESULTS or IMAGE_PENDING state.
        If REQUIRE_RESET_CONFIRM is True, will require confirmation before proceeding.
        If successful, it transitions to IMAGE_PENDING state.
    '''
    def reset(self):
        if self.state == self.State.SAVED_RESULTS or self.state == self.State.IMAGE_PENDING or (self.reset_confirm or not REQUIRE_RESET_CONFIRM):
            self._transition(self.State.IMAGE_PENDING)
            self.algorithm_output = None
            self.loaded_image = None
            return self.OutputCommand.PROCEED
        else:
            return self.OutputCommand.RESET_CONFIRM

    '''
    fn: confirm_reset
        Call to confirm reset if required to call reset(). This should only be called after interface code has gotten approval from the user (e.g. popup).
    ''' 
    def confirm_reset(self):
        # should call reset again after confirmation
        self.reset_confirm = True
        
    def get_loaded_image(self):
        return self.loaded_image

    def get_algorithm_output(self):
        return self.algorithm_output
    
    def get_halt_reason(self):
        return self.halt_reason
    
    def get(self):
        return self.state

'''
typical sequence of operations: (in reality this would be divided out among UI event callbacks)
state = FrontendState(counting_module=..., counting_settings=...)
PROCEED = FrontendState.OutputCommand.PROCEED
HALT = FrontendState.OutputCommand.HALT

command = state.load_image(...)
if command != PROCEED:
    # handle error or reenter a loop

command = state.load_image(...)
if command != PROCEED:
    # handle error or reenter a loop
# fill UI with loaded image, other data to display
    
command = state.prepare_process_image()
if command != PROCEED:
    # handle error or reenter a loop
# lock UI here while processing

command = state.process_image()
# this should take some time and may need to be threaded in real implementation
if command != PROCEED:
    # handle error or reenter a loop
# unlock UI here

command = state.show_results()
if command != PROCEED:
    # handle error or reenter a loop
# display results in UI

command = state.save_results()
if command != PROCEED:
    # handle error or reenter a loop
# update UI to display tate saved

commmand = state.reset() # this will proceed on the first time since state is SAVED_RESULTS
if command == HALT:
    # should not happen here
# go back to initial UI state


state.ready_process_image()
state.process_image()
'''

