import cv2
import glob
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

from utils import from_seconds_to_datetime, sort_function, get_time

class CanFixer:

    def __init__(self, base_path):
        self._base_path = base_path

    def execute(self):
        folders = next(os.walk(self._base_path))[1]

        for folder in folders:
                subfolders = next(os.walk(os.path.join(self._base_path, folder)))[1]
                for subfolder in subfolders:
                    subsubfolders = next(os.walk(os.path.join(self._base_path, folder, subfolder)))[1]
                    for subsubfolder in subsubfolders:
                        folder_path = os.path.join(self._base_path, folder, subfolder, subsubfolder)
                        print("Processing: {}".format(folder_path))
                        can_file = os.path.join(folder_path, "CAN.csv")
                        if os.path.exists(can_file.replace("CAN", "CAN2")):
                            continue
                        data = pd.read_csv(can_file)
                        out_can_file = can_file.replace("CAN", "CAN2")
                        data["rec_time"] = data["UTC"] - data["UTC"][0]
                        data.to_csv(out_can_file)


if __name__ == "__main__":
    can_fixer = CanFixer("/media/brani/DATA/BIORIDIC_PROCESSED")
    can_fixer.execute()