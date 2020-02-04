import cv2
import numpy as np
import torch
from tqdm import tqdm

from biodriver_data_loader import get_class_name_from_id, get_classes


def process_video(video_file, model, output_file, annotations):
    video_input = cv2.VideoCapture(video_file)
    video_out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),
                                int(video_input.get(cv2.CAP_PROP_FPS)), (1280, 720))

    model.eval()

    if not video_input.isOpened():
        raise IOError("Input video not found!")
    index = 0
    for i in tqdm(range(int(video_input.get(cv2.CAP_PROP_FRAME_COUNT)))):
        ret, frame = video_input.read()
        if not ret:
            break
        index += 1
        if index % 5 != 0:
            continue
        frame_resized = cv2.resize(frame, (1280, 720))
        frame_resized_f = frame_resized.astype(np.float32) / 255.
        frame_resized_f = torch.Tensor(frame_resized_f).float().cuda().permute(2, 0, 1)

        out = model([frame_resized_f])[0]
        detected = out["boxes"].detach().cpu().numpy()
        labels = out["labels"].detach().cpu().numpy()
        scores = out["scores"].detach().cpu().numpy()
        image = frame_resized
        # print(scores)

        for i in range(len(labels)):
            if scores[i] < 0.2:
                continue
            bbox = (int(detected[i, 0]), int(detected[i, 1]), int(detected[i, 2]), int(detected[i, 3]))
            image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
            cv2.putText(image, get_class_name_from_id(annotations, labels[i]) + ", SCORE: {}".format(int(100 * scores[i])), (
                bbox[0], bbox[1]-20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 128, 0), 1)

        video_out.write(image)
    video_input.release()
    video_out.release()
