'''
module:     frontend_state
    This implements the state machine for the frontend and handles locking data and user inputs for specific stages.
'''

from enum import Enum

class FrontendState:
    class State(Enum):
        LOADING = 1 # might not be used
        IMAGE_PENDING = 2 # user needs to load from file or camera
        IMAGE_LOADED = 3 # image is loaded and ready for processing
        IMAGE_PROCESSING_READY = 3.5
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

    def __init__(self, *, counting_module, default_counting_settings):
        self.state = self.State.IMAGE_PENDING
        self.lock = False
        self.loaded_image = None
        self.algorithm_output = None
        self.reset_confirm = False

        self.counting_module = counting_module
        self.default_counting_settings = default_counting_settings

    def load_image(self):
        # halt if state is not IMAGE_PENDING
        if self.state == self.State.IMAGE_PENDING:
            self._transition(self.State.IMAGE_PENDING)
        else:
            return self.OutputCommand.HALT
        
        self.lock = True
        # load image here
        self.lock = False

    # intermediate step to allow UI to go into greyed out processing state
    def ready_process_image(self):
        if self.state == self.State.IMAGE_LOADED:
            self._transition(self.State.IMAGE_PROCESSING_READY)
        else:
            return self.OutputCommand.HALT
    
    # actual image processing step
    def process_image(self):
        if self.state == self.State.IMAGE_PROCESSING_READY and not self.lock:
            self._transition(self.State.IMAGE_PROCESSING)
            self.lock = True
            # perform image processing here
            # self.loaded_image should be set before calling this
            self.algorithm_output = self.counting_module.process_image(self.loaded_image, self.default_counting_settings)
            self.lock = False
        else:
            return self.OutputCommand.HALT

    def show_results(self):
        if self.state == self.State.IMAGE_PROCESSING and not self.lock:
            self._transition(self.State.SHOWING_RESULTS)
        else:
            return self.OutputCommand.HALT

    def reset(self):
        if self.state == self.State.SAVED_RESULTS or self.state == self.State.IMAGE_PENDING or self.reset_confirm:
            self._transition(self.State.IMAGE_PENDING)
            self.algorithm_output = None
            self.loaded_image = None
            return self.OutputCommand.PROCEED
        else:
            return self.OutputCommand.RESET_CONFIRM
        
    def confirm_reset(self):
        # should call reset again after confirmation
        self.reset_confirm = True
        
    def get_loaded_image(self):
        return self.loaded_image

    def get_algorithm_output(self):
        return self.algorithm_output
    

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

