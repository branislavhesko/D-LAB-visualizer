import cv2
import glob
import logging
logging.basicConfig(filename="log.log", format='%(filename)s: %(message)s',
                    level=logging.INFO)
import os
import pandas as pd
from tqdm import tqdm


class ProcessedOutputStats:


    def __init__(self, path):
        self._path = path
        self._logger = logging.getLogger(__name__)

    def execute(self):
        folders = next(os.walk(self._path))[1]
        
        for folder in folders:
            subfolders = next(os.walk(os.path.join(self._path, folder)))[1]
            for subfolder in subfolders:
                subsubfolders = next(os.walk(os.path.join(self._path, folder, subfolder)))[1]
                for subsubfolder in subsubfolders:
                    self._logger.info(f"Processing PATH: {os.path.join(self._path, folder, subfolder, subsubfolder)}.")
                    biosignal_file = glob.glob(os.path.join(self._path, folder, subfolder, subsubfolder, "biosignals.csv"))
                    biosignal_file = biosignal_file[0] if any(biosignal_file) else None
                    can_signal_file = glob.glob(os.path.join(self._path, folder, subfolder, subsubfolder, "CAN.csv"))[0]
                    video_file = glob.glob(os.path.join(self._path, folder, subfolder, subsubfolder, "output_video.*"))[0]
                    left_file = glob.glob(os.path.join(self._path, folder, subfolder, subsubfolder, "left.mp4"))
                    left_file = left_file[0] if any(left_file) else None
                    right_file = glob.glob(os.path.join(self._path, folder, subfolder, subsubfolder, "right.mp4"))
                    right_file = right_file[0] if any(right_file) else None

                    for f in [video_file, left_file, right_file]:
                        if f is None:
                            continue
                        video = cv2.VideoCapture(f)
                        fps = video.get(cv2.CAP_PROP_FPS) if video.get(cv2.CAP_PROP_FPS) > 1 else -1
                        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
                        if frame_count < 0:
                            counter = 0
                            while video.read()[0]:
                                counter += 1
                            frame_count = counter
                        self._logger.info(f"FILE: {f}, length: {frame_count / fps}, fps: {fps}")
                        video.release()
                    can = pd.read_csv(can_signal_file)
                    duration = can["UTC"].values[-1] - can["UTC"].values[0]
                    self._logger.info(f"CAN SIGNAL: {can_signal_file}, shape: {can.shape}, duration: {duration / 1000.}")
                    if biosignal_file is not None:
                        bio = pd.read_csv(biosignal_file, delimiter="\t", skiprows=1)
                        dur = bio["rec_time"].values[-1]
                        self._logger.info(f"BIO SIGNAL: {biosignal_file}, shape: {bio.shape}, duration: {dur}")

if __name__ == "__main__":
    p = ProcessedOutputStats("/media/brani/DATA/BIORIDIC_PROCESSED")
    p.execute()