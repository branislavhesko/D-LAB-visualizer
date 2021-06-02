import logging
import os
import multiprocessing

import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from utils import detect_eyetracker_in_video


def compute(path):
    video_file =  os.path.join(path, "output_video.mkv")
    text_file = os.path.join(path, "eyetracker_positions.csv")
    if not os.path.exists(text_file):
        detect_eyetracker_in_video(video_file, text_file, "./skuska2.png")


class DetectorEyetrackerInVideos:

    def __init__(self, path):
        self._path = path
        self._logger = logging.getLogger(self.__class__.__name__)

    def execute(self):
        folders = next(os.walk(self._path))[1]
        paths = []
        for folder in folders:
            subfolders = next(os.walk(os.path.join(self._path, folder)))[1]
            for subfolder in subfolders:
                subsubfolders = next(os.walk(os.path.join(self._path, folder, subfolder)))[1]
                for subsubfolder in subsubfolders:
                    print(f"Processing PATH: {os.path.join(self._path, folder, subfolder, subsubfolder)}.")

                    paths.append(os.path.join(self._path, folder, subfolder, subsubfolder))
        with multiprocessing.Pool(os.cpu_count()) as pool:
            pool.map(compute, paths)



if __name__ == "__main__":
    DetectorEyetrackerInVideos("/media/brani/DATA/BIORIDIC_PROCESSED").execute()