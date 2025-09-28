
from user_interface.frontend_display import FrontendDisplay
def main():
    #call frontend
    pass


if __name__ == "__main__":
    main()
    counting_settings = None #PUT FILEPATH HERE EMPTY FOR NOW WILL BE NORMAL SETTINGS
    default_settings = None #ALSO PUT FILEPATH HERE FOR DEFAULT SETTINGS
    display = FrontendDisplay(counting_settings=counting_settings)
    display.start()