import cv2
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
from datetime import datetime
import os
from biodriver_data_loader import get_class_name_from_id, get_classes
from transforms import Compose, Scale, Normalize, HorizontalFlip, VerticalFlip, Rotate
from biodriver_data_loader import BioDriverLoader


loader = BioDriverLoader("./data/backup")
folder = "./classification_day"
if not os.path.exists(folder):
    os.mkdir(folder)

for img, bbox, label in tqdm(loader):
    img = img.permute(1, 2, 0).cpu().numpy() * 255
    img = img.astype(np.uint8)
    bbox = bbox.cpu().numpy()
    label = label.cpu().numpy()
    for i in range(bbox.shape[0]):
        class_ = get_class_name_from_id(loader.annotations, label[i])
        if "znacka" in class_:
            if (bbox[i, 3] - bbox[i, 1]) * (bbox[i, 2] - bbox[i, 0]) < 500:
                continue
            time_stamp = datetime.now().strftime("%m_%d_%Y$%H_%M_%S_%f_")

            tile = img[int(bbox[i, 1]): int(
                bbox[i, 3]), int(bbox[i, 0]): int(bbox[i, 2]), :]
            cv2.imwrite(os.path.join(folder, time_stamp + f"{i}.png"), tile[:, :, ::-1])