'''
Project Thames Bee Counting Tool
authors: Connor Clouse, John Pratt, Henry Shaw
version: 0.1
'''

from app.frontend_display import FrontendDisplay
import time

# if __name__ == "__main__":
#     import sys
#     if not ('src' in sys.path):
#         sys.path.append('src')


def main():
    # actual main function
    '''
    # for program loop:
    1. Have user select or use new spreadsheet to work out of. 
    (this is actually easier with CLI since they should already be in the working directory.)
    2. Await user input action:
        a. Manually enter a bee sample.
        b. Process a bee sample from image file.
        c. Process a bee sample from webcam.
        d. Exit, save and close. (or variations of this)
    3. Execute selection action, return to step 2.
    '''
    while True:
        print("counting bees smh")
        time.sleep(1)

# prototype application entry point:
print("Bee Count Tool: starting ...")

display = FrontendDisplay()
display.main = main
display.start()

print("Bee Count Tool: exiting ...")

'''
Strategies for error handling:
'''