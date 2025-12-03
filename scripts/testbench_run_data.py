'''
module: testbench_run_data.py
description:
    Class for holding data about a test run of the counting algorithm.
    Also handles loading and storing results.
'''
import os
import datetime
from collections import OrderedDict
import json

class TestbenchContourData:
    def __init__(self, contour):
        self.area = contour.area
        self.bounding_box = contour.bounding_box  # (x, y, w, h)
        self.centroid = contour.centroid  # (cx, cy)
        self.type = contour.get_type().name
        self.source = contour.source
    
    def ser_to_dict(self):
        return {
            "area": self.area,
            "bounding_box": self.bounding_box,
            "centroid": self.centroid,
            "type": self.type,
            "source": self.source
        }
    
    @staticmethod
    def des_from_dict(dict_data):
        contour_data = TestbenchContourData.__new__(TestbenchContourData)
        # write class fields from dictionary (should be ok)
        contour_data.__dict__.update(dict_data)
        return contour_data




class TestbenchRunData:

    IO_DIR = "io/testbench_runs"

    def __init__(self, algorithm_output, input_image_path, postfix="STD", algorithm_version="unknown", tags=None):
        # initilize created timestamp
        self.created_timestamp = datetime.datetime.now()
        self.input_image_path = input_image_path
        self.algorithm_version = algorithm_version
        self.postfix = postfix
        self.tags = set(tags) if tags else set()

        self.bee_count = algorithm_output.bee_count
        self.single_bee_count = algorithm_output.single_bee_count
        self.clump_count = algorithm_output.clump_count


        # save output contours into serdes form
        self.contours = []
        for contour in algorithm_output.contours.get_contours():
            contour_data = TestbenchContourData(contour)
            self.contours.append(contour_data)

    def save(self):
        # create json dictionary
        serialized = OrderedDict()
        serialized["input_image_path"] = self.input_image_path
        serialized["algorithm_version"] = self.algorithm_version
        serialized["created_timestamp"] = self.created_timestamp.isoformat()
        serialized["bee_count"] = self.bee_count
        serialized["single_bee_count"] = self.single_bee_count
        serialized["clump_count"] = self.clump_count
        serialized["contours"] = [c.ser_to_dict() for c in self.contours]

        file_name = os.path.splitext(os.path.basename(self.input_image_path))[0] 
        file_name += "_" + self.postfix + ".json"
        save_path = os.path.join(self.IO_DIR, file_name)

        # create io directory if it doesn't exist
        os.makedirs(self.IO_DIR, exist_ok=True)

        with open(save_path, 'w') as f:
            json.dump(serialized, f, indent=4)

    @staticmethod
    def load(name=None, file_name = None, postfix="STD"):
        if file_name is not None:
            load_path = os.path.join(TestbenchRunData.IO_DIR, file_name)
        else:
            file_name = name + "_" + postfix + ".json"
        load_path = os.path.join(TestbenchRunData.IO_DIR, file_name)
        with open(load_path, 'r') as f:
            dict_data = json.load(f)
            run_data = TestbenchRunData.__new__(TestbenchRunData)
            run_data.__dict__.update(dict_data)
            # deserialize contours
            run_data.contours = [TestbenchContourData.des_from_dict(cdict) for cdict in dict_data["contours"]]
            return run_data

        
    def check_tag(self, tag):
        return tag in self.tags
    
    def check_tags(self, required_tags):
        return required_tags.issubset(self.tags)

    def load_batch(self, has_tag=None, has_tags=None, postfix=None):
        run_data_list = []

        for file_name in os.listdir(self.IO_DIR):
            if not file_name.endswith(".json"):
                continue
            
            run_data = TestbenchRunData.load(file_name=file_name)
            if has_tag and not run_data.check_tag(has_tag):
                continue
            if has_tags and not run_data.check_tags(has_tags):
                continue
            if postfix and run_data.postfix != postfix:
                continue
            run_data_list.append(run_data)
        return run_data_list

    
