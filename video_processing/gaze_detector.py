import logging
import os

import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from utils import detect_eyetracker_in_video


class DetectorEyetrackerInVideos:

    def __init__(self, path):
        self._path = path

    def execute(self):
        folders = next(os.walk(self._path))[1]
        
        for folder in folders:
            subfolders = next(os.walk(os.path.join(self._path, folder)))[1]
            for subfolder in subfolders:
                subsubfolders = next(os.walk(os.path.join(self._path, folder, subfolder)))[1]
                for subsubfolder in subsubfolders:
                    print(f"Processing PATH: {os.path.join(self._path, folder, subfolder, subsubfolder)}.")
                    path = os.path.join(self._path, folder, subfolder, subsubfolder)


if __name__ == "__main__":
    DetectorEyetrackerInVideos("/media/brani/DATA/BIORIDIC_PROCESSED").execute()