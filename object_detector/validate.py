import cv2
import numpy as np
import torch

from biodriver_data_loader import get_class_name_from_id


@torch.no_grad()
def validate(model, loader, dataset):
    model.eval()
    for index, (data, gt, label) in enumerate(loader):
        data = torch.squeeze(data).cuda()
        out = model([data])[0]

        image = data.cpu().permute([1, 2, 0]).numpy() * 255
        image = image.astype(np.uint8)
        detected = out["boxes"].cpu().numpy()
        labels = out["labels"].cpu().numpy()
        scores = out["scores"].cpu().numpy()
        print(scores)

        for i in range(len(labels)):
            if scores[i] < 0.05:
                continue
            bbox = (int(detected[i, 0]), int(detected[i, 1]), int(detected[i, 2]), int(detected[i, 3]))
            image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
            cv2.putText(image, get_class_name_from_id(dataset.annotations, labels[i]), (
                bbox[0], bbox[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)
        cv2.imwrite("output{}.png".format(index), image)
