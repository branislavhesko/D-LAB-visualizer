from copy import deepcopy
import glob
import numpy as np
import os
import pandas as pd

from biosignalsplux_loader import BiosignalsPluxLoader
from utils import get_time


class PreprocessBiosignalData:

    def __init__(self, base_path, output_path):
        self.base_path = base_path
        self.output_path = output_path

    def execute(self):
        folders = next(os.walk(self.base_path))[1]
        
        for folder in folders:
            subfolders = next(os.walk(os.path.join(self.base_path, folder)))[1]
            for subfolder in subfolders:
                subsubfolders = next(os.walk(os.path.join(self.base_path, folder, subfolder)))[1]
                for subsubfolder in subsubfolders:
                    print("Processing {}.".format(os.path.join(self.base_path, folder, subfolder, subsubfolder)))
                    biosignals = sorted(glob.glob(os.path.join(
                        self.base_path, folder, subfolder, subsubfolder, "opensignal*.txt")))
                    biosignal_output = None
                    start_time = None
                    for biosignal in biosignals:
                        loader = BiosignalsPluxLoader()
                        loader.load_file(biosignal)
                        time_ = get_time(loader.header["time"])
                        start_time = time_ if start_time is None else start_time
                        loader.generate_rec_time(time_ - start_time)
                        if biosignal_output is None:
                            biosignal_output = deepcopy(loader)
                            start_time = get_time(biosignal_output.header["time"])
                        else:
                            biosignal_output.data = pd.concat([biosignal_output.data, loader.data], sort=False)
                    if biosignal_output is not None:
                        if not os.path.exists(os.path.join(self.output_path, folder, subfolder, subsubfolder)):
                            os.makedirs(os.path.join(self.output_path, folder, subfolder, subsubfolder))
                        biosignal_output.save(os.path.join(self.output_path, folder, subfolder, subsubfolder, "biosignals.csv"))



if __name__ == "__main__":
    p = PreprocessBiosignalData("/media/brani/DATA/BIORIDIC_PROCESSED", "/media/brani/DATA/BIORIDIC_PROCESSED")
    p.execute()