from enum import auto, Enum
import glob
import os

import numpy as np
from PIL import Image
from torch.utils import data
import torch
from tqdm import tqdm

from transforms import Compose, Rotate, Scale, Normalize


def get_classes(file: str) -> dict:
    classes = {}
    i = 0
    with open(file, "r") as f:
        for line in f:
            classes[line[:line.find("\n")]] = i
            i += 1
    print(classes)
    return classes


def get_class_name_from_id(annotations: dict, id: int) -> str:
    for key in annotations.keys():
        if annotations[key] == id:
            return key
    return "None"


class ItemEnum(Enum):
    IMAGE_PATH = auto()
    LABEL = auto()
    BOX_COORDS = auto()


class BioDriverLoader(data.Dataset):
    label_file_name = "data/classes.txt"
    detected_file_name = "data/detected.txt"
    img_subfolder = "data/images"
    name = "BIODRIVER"
    data_size = np.array((1280, 720, 1280, 720))

    def __init__(self, root=""):
        self.detected_file = os.path.join(root, self.detected_file_name)
        self.annotations = get_classes(os.path.join(root, self.label_file_name))
        self._root_dir = root
        self.item_dict = {
            ItemEnum.IMAGE_PATH: [],
            ItemEnum.BOX_COORDS: [],
            ItemEnum.LABEL: []
        }
        self.load_label_file()
        self.transform = Compose([
            Scale(0.1),
            Rotate(),
        ])

    def __len__(self):
        return len(self.item_dict[ItemEnum.IMAGE_PATH])

    def __getitem__(self, index: int):
        image = np.array(Image.open(self.item_dict[ItemEnum.IMAGE_PATH][index])).astype(np.float32)
        image = image.astype(np.float32) / 255.
        label = self.item_dict[ItemEnum.LABEL][index]
        box_coords = np.array(self.item_dict[ItemEnum.BOX_COORDS][index])
        image, box_coords = self.transform(image, box_coords)
        output = torch.from_numpy(image.astype(np.float32)).permute(
            [2, 0, 1]), torch.from_numpy(box_coords).float(), torch.Tensor(label).long()
        return output

    def load_label_file(self):
        with open(self.detected_file, "r") as f:
            for line in f:
                line = line[:-1]
                items = line.split("\t")
                if items[3] == "None":
                    continue

                img_name = items[0] + "_" + items[2] + "_" + items[1] + ".png"
                img_name = os.path.join(self._root_dir, self.img_subfolder, img_name)
                if not os.path.exists(img_name):
                    print(img_name)
                    continue
                test = np.array(Image.open(img_name))
                if test.dtype != np.uint8:
                    continue
                box_coord = [float(item) for item in items[4:]]
                if img_name not in self.item_dict[ItemEnum.IMAGE_PATH]:
                    self.item_dict[ItemEnum.IMAGE_PATH].append(img_name)
                    self.item_dict[ItemEnum.LABEL].append([self.annotations[items[3]]])
                    self.item_dict[ItemEnum.BOX_COORDS].append([[box_coord[0], box_coord[1],
                                                                 box_coord[0] + box_coord[2],
                                                                 box_coord[1] + box_coord[3]]])
                else:
                    index = self.item_dict[ItemEnum.IMAGE_PATH].index(img_name)
                    self.item_dict[ItemEnum.LABEL][index].append(self.annotations[items[3]])
                    self.item_dict[ItemEnum.BOX_COORDS][index].append(
                        [box_coord[0], box_coord[1], box_coord[0] + box_coord[2], box_coord[1] + box_coord[3]])

    def __str__(self):
        return str(self.item_dict)


if __name__ == "__main__":
    print(get_classes("./data/classes.txt"))
    b = BioDriverLoader()
    b.load_label_file()
    print(b[0][2].size())
