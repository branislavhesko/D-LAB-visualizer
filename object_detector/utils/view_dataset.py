import cv2
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm

from biodriver_data_loader import get_class_name_from_id, get_classes
from transforms import Compose, Scale, Normalize, HorizontalFlip, VerticalFlip, Rotate


def view_detection_dataset(loader, annotations):
    transform = Compose([
        Scale(0.2),
        Rotate()
    ])
    for img, bbox, label in tqdm(loader):
        img = img.permute(1, 2, 0).cpu().numpy()
        bbox = bbox.cpu().numpy()
        label = label.cpu().numpy()
        img, bbox = transform(img, bbox)
        for i in range(bbox.shape[0]):
            img = cv2.rectangle(img, (int(bbox[i, 0]), int(
                bbox[i, 1])), (int(bbox[i, 2]), int(bbox[i, 3])), (255, 0, 0), 2)
            print(bbox.shape)
            cv2.putText(img, get_class_name_from_id(annotations, label[i]), (
                int(bbox[i, 0]), int(bbox[i, 1]-20)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)

        plt.figure(dpi=120)
        plt.imshow(img, cmap="jet")
        plt.waitforbuttonpress(0)
        plt.close()


if __name__ == "__main__":
    from biodriver_data_loader import BioDriverLoader
    loader = BioDriverLoader("./")
    view_detection_dataset(loader, loader.annotations)
