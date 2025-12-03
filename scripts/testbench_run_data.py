'''
module: testbench_run_data.py
description:
    Class for holding data about a test run of the counting algorithm.
    Also handles loading and storing results.
'''
import datetime

class TestbenchRunData:

    IO_DIR = "io/testbench_runs"

    def __init__(self, algorithm_output, input_image_path, postfix="STD", algorithm_version="unknown"):
        # initilize created timestamp
        self.created_timestamp = datetime.datetime.now()
        self.input_image_path = input_image_path
        self.algorithm_version = algorithm_version
        self.postfix = postfix

        self.bee_count = algorithm_output.bee_count
        self.single_bee_count = algorithm_output.single_bee_count
        self.clump_count = algorithm_output.clump_count


        # save output contours into serdes form
        self.contours = []

    def save():
        pass

    @staticmethod
    def load():
        pass

    
    