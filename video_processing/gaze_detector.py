import logging
import os

import cv2
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


class GazeConfig:
    min_duration = 0.120 # s
    min_speed = 200 # px / frame
    mean_filter_size = 7
    fps = 30


class GazeAnalyzer:
    def __init__(self, csv_file) -> None:
        self.dataframe = pd.read_csv(csv_file, delimiter="\t")
        self.x = self.dataframe.values[:, 1]
        self.y = self.dataframe.values[:, 2]

    def execute(self, config: GazeConfig, path):
        self.x = np.convolve(self.x, np.ones((config.mean_filter_size)), "same")
        self.y = np.convolve(self.y, np.ones((config.mean_filter_size)), "same")

        velocity = np.sqrt((self.x[1:] - self.x[:-1]) ** 2 + (self.y[1:] - self.y[:-1]) ** 2)
        velocity_under_threshold = velocity < config.min_speed
        velocity_cumsum = np.cumsum(velocity_under_threshold)
        velocity_borders = velocity_cumsum[1:] - velocity_cumsum[:-1]
        gaze_borders = np.where(velocity_borders == 0)[0]
        gazes = np.stack((gaze_borders[:-1], gaze_borders[1:], (gaze_borders[1:] - gaze_borders[:-1])))
        gazes = gazes[:, gazes[-1, :] > int(config.fps * config.min_duration)]
        gazes = pd.DataFrame(data={"frame_start": gazes[0, :], "frame_end": gazes[1, :], "duration": gazes[2, :]})

        xs = []
        ys = []
        for idx, gaze in gazes.iterrows():
            xs.append(np.median(self.dataframe.values[gaze.frame_start: gaze.frame_end, 1]))
            ys.append(np.median(self.dataframe.values[gaze["frame_start"]: gaze["frame_end"], 2]))

        gazes["x"] = xs
        gazes["y"] = ys
        gazes = gazes.loc[(gazes["x"] > 1) & (gazes["y"] > 1), :]
        gazes.to_csv(os.path.join(path, "detected_gazes_from_video.csv"))


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
                    analyzer = GazeAnalyzer(os.path.join(path, "eyetracker_positions.csv"))
                    analyzer.execute(GazeConfig(), path)


if __name__ == "__main__":
    DetectorEyetrackerInVideos("/media/brani/DATA/BIORIDIC_PROCESSED").execute()