import cv2
import glob
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

from utils import from_seconds_to_datetime, sort_function


class PreprocessData:
    UTC = "UTC"
    FPS = 30
    FRAME_SIZE= (1280, 720)
    FRAME_SIZE_EYE = (384, 288)

    def __init__(self, base_path, output_path):
        self._base_path = base_path
        self._output_path = output_path
        self._new_video = None
        self._new_left = None
        self._new_right = None
        self._frame_size = None

    def execute(self):
        folders = next(os.walk(self._base_path))[1]
        
        for folder in folders:
            subfolders = next(os.walk(os.path.join(self._base_path, folder)))[1]
            for subfolder in subfolders:
                subsubfolders = next(os.walk(os.path.join(self._base_path, folder, subfolder)))[1]
                for subsubfolder in subsubfolders:
                    folder_path = os.path.join(self._base_path, folder, subfolder, subsubfolder)
                    os.makedirs(folder_path, exist_ok=True)
                    csv_files = sorted(glob.glob(os.path.join(
                        folder_path, "*Recording*.txt")), key=sort_function)
                    video_files_orig = sorted(glob.glob(os.path.join(
                        folder_path, "*Scene Cam_*.mp4")), key=sort_function)
                    video_files_left = sorted(glob.glob(os.path.join(
                        folder_path, "*Eye Cam - Left.mp4")), key=sort_function)
                    video_files_right = sorted(glob.glob(os.path.join(
                        folder_path, "*Eye Cam - Right.mp4")), key=sort_function)
                    start_time = -1
                    end_time = -1
                    output_data_frame = None
                    output_path_video, output_path_data, output_path_left, output_path_right = self._get_output_path(
                        folder, subfolder, subsubfolder)
                    if os.path.exists(output_path_data):
                        print("THIS FOLDER IS ALREADY PROCESSED: {}.".format(output_path_data))
                        continue
                    print("output video: {}".format(output_path_video))
                    self._new_video = cv2.VideoWriter(output_path_video, cv2.VideoWriter_fourcc(*"H264"), self.FPS, 
                                                      self.FRAME_SIZE)
                    self._new_left = cv2.VideoWriter(output_path_left, cv2.VideoWriter_fourcc(*"H264"), self.FPS, 
                                                      self.FRAME_SIZE_EYE)
                    self._new_right = cv2.VideoWriter(output_path_right, cv2.VideoWriter_fourcc(*"H264"), self.FPS, 
                                                      self.FRAME_SIZE_EYE)
                    for csv_file in csv_files:
                        base_name = csv_file[:max(csv_file.find("AM"), csv_file.find("PM")) + 2]
                        video_left_file = [left for left in video_files_left if left.find(base_name) >= 0]
                        video_orig_file = [orig for orig in video_files_orig if orig.find(base_name) >= 0]
                        video_right_file = [right for right in video_files_right if right.find(base_name) >= 0]

                        if not any(video_orig_file) and not any(video_left_file) and not any(video_right_file):
                            continue

                        print(csv_file)
                        csv_data = pd.read_csv(csv_file, delimiter="\t")
                        if output_data_frame is None:
                            output_data_frame = csv_data
                        else:
                            output_data_frame = pd.concat([output_data_frame, csv_data])
                        start_time = csv_data[self.UTC].values[0] / 1000.
                        time_gap = (start_time - end_time) if end_time > 0 else 0
                        end_time = csv_data[self.UTC].values[-1] / 1000.
                        print(time_gap)
                        self._frame_size = self.FRAME_SIZE
                        self._new_video = self.process_video(self._new_video, video_orig_file, time_gap)
                        self._frame_size = self.FRAME_SIZE_EYE

                        if len(video_left_file):
                            self._new_left = self.process_video(self._new_left, video_left_file, time_gap)
                        if len(video_right_file):
                            self._new_right = self.process_video(self._new_right, video_right_file, time_gap)
                    output_data_frame.to_csv(output_path_data)
                    self._new_video.release()
                    self._new_left.release()
                    self._new_right.release()

    def process_video(self, new_video, video_file, time_gap):
        old_video = cv2.VideoCapture(video_file[0])
        old_fps=old_video.get(cv2.CAP_PROP_FPS)
        if old_fps < 10:
            return new_video

        frame_width, frame_height = int(old_video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(old_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("Video file: {}, fps: {}, size: {}:{}.".format(video_file[0], old_fps, frame_width, frame_height))
        new_video = self.insert_empty_frames(new_video, time_gap, frame_height=frame_height, frame_width=frame_width)
        if old_fps < self.FPS:
            new_video = self.insert_video_low_fps(new_video, old_video, old_fps=old_fps, fps=self.FPS)
        else:
            mask = self.generate_mask(old_fps=old_fps, fps=self.FPS, total_frames=old_video.get(
                cv2.CAP_PROP_FRAME_COUNT))
            new_video = self.insert_video(new_video, old_video, mask)
        return new_video

    def insert_video(self, new_video, old_video, mask=None):
        for i in tqdm(range(int(old_video.get(cv2.CAP_PROP_FRAME_COUNT)))):
            ret, frame = old_video.read()
            if ret and mask[i]:
                new_video.write(cv2.resize(np.copy(frame), self._frame_size))
        return new_video

    @staticmethod
    def generate_mask(old_fps, fps, total_frames):
        mask = np.ones(int(total_frames), dtype=bool)
        to_preserve = int(np.round(total_frames * fps / old_fps))

        if total_frames == to_preserve:
            return mask

        coefficient = int(np.ceil(total_frames / (total_frames - to_preserve)))

        if coefficient >= to_preserve:
            return mask

        mask[::coefficient] = 0

        preserved = np.sum(mask)
        if preserved == to_preserve:
            return mask
        coefficient = int(np.ceil(total_frames / (preserved - to_preserve)))
        mask[::coefficient] = 0
        random_choice = np.random.choice(int(total_frames), int(np.round(abs(np.sum(mask) - to_preserve))), 
                                         p=mask/np.sum(mask), replace=False)
        mask[random_choice] = 0
        print("P: {}, M: {}".format(to_preserve, np.sum(mask)))
        return mask
    
    def _get_output_path(self, folder, subfolder, subsubfolder):
        folder_dir = os.path.join(self._output_path, folder, subfolder, subsubfolder)
        print("FOLDER DIR: {}".format(folder_dir))
        if not os.path.exists(folder_dir):
            os.makedirs(folder_dir)
        return (os.path.join(folder_dir, "output_video.mkv"), os.path.join(folder_dir, "CAN.csv"), 
                os.path.join(folder_dir, "left.mp4"), os.path.join(folder_dir, "right.mp4"))

    def insert_video_low_fps(self, new_video, old_video, old_fps, fps):
        total_frames = old_video.get(cv2.CAP_PROP_FRAME_COUNT)
        num_frames_needed = total_frames * fps / old_fps
        random_repetitions = np.random.choice(int(total_frames), int(np.round(abs(total_frames - num_frames_needed))), replace=True)
        print("P: {}, M: {}".format(total_frames, num_frames_needed))
        for idx in tqdm(range(int(total_frames))):
            ret, frame = old_video.read()
            if ret:
                new_video.write(cv2.resize(np.copy(frame), self._frame_size))
                if idx in random_repetitions:
                    print("Duplicating: {}".format(idx))
                    new_video.write(cv2.resize(np.copy(frame), self._frame_size))
        return new_video

    def insert_empty_frames(self, new_video, time_gap, frame_width, frame_height):
        number_of_frames = time_gap * self.FPS
        for _ in range(int(np.round(number_of_frames))):
            frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            new_video.write(cv2.resize(frame, self._frame_size))
        return new_video

    def _number_of_empty_frames(self, length, fps):
        return int(length * fps)

    def _compose_output_path(self):
        pass

    def _compose_data_frames(self, data_frames_list):
        return pd.concat(data_frames_list)


if __name__ == "__main__":
    p = PreprocessData("/home/brani/Desktop/BIORIDICE_PROCESSED", "/media/brani/DATA/BIORIDIC_PROCESSED")
    p.execute()