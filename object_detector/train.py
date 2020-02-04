from tqdm import tqdm
import cv2
import colorama
import numpy as np
import torch
from torchvision.models.detection.faster_rcnn import fasterrcnn_resnet50_fpn, FastRCNNPredictor

from biodriver_data_loader import get_class_name_from_id, get_classes, BioDriverLoader
from process_video import process_video
from validate import validate


class Configuration:
    checkpoint = "./model.pth"
    WITH_CUDA = True
    num_classes = 17


def get_model_fastrcnn(num_classes, ckpt):
    model = fasterrcnn_resnet50_fpn(pretrained=True)
    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, Configuration.num_classes)

    if ckpt is not None:
        model.load_state_dict(torch.load(ckpt))
    return model


def train(model, loader, dataset, WITH_CUDA=False):
    model.cuda() if WITH_CUDA else None
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=0.001, momentum=0.9, weight_decay=1e-4)

    model.train()

    for i in range(100):
        model.train()
        for index, (data, gt, label) in tqdm(enumerate(loader)):
            data = torch.squeeze(data).cuda() if WITH_CUDA else torch.squeeze(data)
            gt = gt[0, :, :].cuda() if WITH_CUDA else gt[0, :, :]
            label = label[0, :].cuda() if WITH_CUDA else label[0, :]
            target = {
                "boxes": gt,
                "labels": label,
                "image_id": torch.Tensor([index]).long(),
                "area": (gt[:, 3] - gt[:, 1]) * (gt[:, 2] - gt[:, 0]),
                "is_crowd": torch.zeros(label.size()[0])
            }
            output = model([data], [target])
            output_loss = sum(loss for loss in output.values())
            optimizer.zero_grad()
            output_loss.backward()
            optimizer.step()
        torch.save(model.state_dict(), "model.pth")
        torch.save(optimizer.state_dict(), "opt_model.pth")
        if i % 20 == 0:    
            process_video("3.mp4", model, "out{}.avi".format(i), dataset.annotations)

    validate(model, loader, dataset)


if __name__ == "__main__":
    model = get_model_fastrcnn(2, Configuration.checkpoint)
    dataset = BioDriverLoader("./")
    model.cuda()
    process_video("./test.mp4", model, "output_test_.avi", dataset.annotations)
    exit(-1)
    loader = torch.utils.data.DataLoader(dataset, batch_size=1, num_workers=0, shuffle=False)
    train(model, loader, dataset, Configuration.WITH_CUDA)
