import datetime
import math

import cv2
import tqdm
import numpy as np


def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))


def from_seconds_to_datetime(seconds_from_epoch):
    return datetime.datetime.fromtimestamp(seconds_from_epoch)


def sort_function(string: str):
    recording_start = string.find("Recording")
    string_part = string[recording_start - 4: recording_start - 1]
    string_part = ''.join(i for i in string_part if i.isdigit())
    return float(string_part)


def get_time(time):
    time_parts = time.split(":")
    time_parts = [float(t) for t in time_parts]
    time_parts[0] = time_parts[0] if time_parts[0] > 12 else time_parts[0] + 24
    return time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]


def detect_eyetracker_in_video(video_file, file_name, template_file):
    template = cv2.imread(template_file)
    template[template[:, :, 2] < 220] = 0
    video = cv2.VideoCapture(video_file)
    file = open(file_name, "w")
    file.write("\t".join(["frame_id", "x", "y"]) + "\n")
    ret = True
    for idx in tqdm.tqdm(range(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))):
        ret, frame = video.read()
        frame[(frame[:, :, 2] < 200) | (frame[:, :, 0] > 40) | (frame[:, :, 1] > 40), :] = 0
        matched = cv2.matchTemplate(frame, template, method=cv2.TM_CCOEFF_NORMED)
        maximum = np.unravel_index(np.argmax(matched), matched.shape)
        maximum = maximum[::-1]
        file.write("\t".join([str(idx), ] + list(map(str, maximum))) + "\n")
    file.close()