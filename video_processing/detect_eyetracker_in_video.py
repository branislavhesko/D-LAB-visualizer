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
        self._logger = logging.getLogger(self.__class__.__name__)

    def execute(self):
        folders = next(os.walk(self._path))[1]
        
        for folder in folders:
            subfolders = next(os.walk(os.path.join(self._path, folder)))[1]
            for subfolder in subfolders:
                subsubfolders = next(os.walk(os.path.join(self._path, folder, subfolder)))[1]
                for subsubfolder in subsubfolders:
                    print(f"Processing PATH: {os.path.join(self._path, folder, subfolder, subsubfolder)}.")
                    path = os.path.join(self._path, folder, subfolder, subsubfolder)
                    video_file =  os.path.join(path, "output_video.mkv")
                    text_file = os.path.join(path, "eyetracker_positions.csv")
                    if not os.path.exists(text_file):
                        detect_eyetracker_in_video(video_file, text_file, "./skuska2.png")


if __name__ == "__main__":
    DetectorEyetrackerInVideos("/media/brani/DATA/BIORIDIC_PROCESSED").execute()