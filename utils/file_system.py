'''
module: file_system.py
    Utility functions for accessing files. 
    Mainly want this for the case of users executing this program from 
    undetermined directories.
'''

'''
fn: get_project_dir()
    returns the root folder of this project (the parent of this scripts directory)
'''
import os.path

def get_project_dir():
    this_file_path = __file__
    # not the greatest since now this file cannot move, but should do
    return os.path.dirname(os.path.dirname(this_file_path))

if __name__ == "__main__":
    print(get_project_dir())
    


