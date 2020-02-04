"""
All of these transforms suppose bbox in form (x_min, y_min, x_max, y_max).
"""
import numpy as np
import cv2
from skimage.transform import rescale, rotate


class Compose:
    def __init__(self, transforms):
        self._transforms = transforms

    def __call__(self, img, bbox):
        for transform in self._transforms:
            img, bbox = transform(img, bbox)
        return img, bbox


# TODO: this is broken, when flipping, x_end becomes smaller...
class HorizontalFlip:
    def __call__(self, img, bboxs):
        img_shape = img.shape
        bboxs[:, 1] = img_shape[0] - bboxs[:, 1]
        bboxs[:, 3] = img_shape[0] - bboxs[:, 3]
        return img[::-1, :, :], bboxs


# TODO: this is broken, when flipping, x_end becomes smaller...
class VerticalFlip:
    def __call__(self, img, bboxs):
        img_shape = img.shape
        bboxs[:, 0] = img_shape[1] - bboxs[:, 0]
        bboxs[:, 2] = img_shape[1] - bboxs[:, 2]
        return img[:, ::-1, :], bboxs


class Scale:
    def __init__(self, scale_coef=0.2):
        self._scale_coef = scale_coef

    def __call__(self, img, bboxs):
        img_shape = np.array(img.shape)
        scale = 1. + np.random.rand(1) * self._scale_coef
        bboxs_scaled = bboxs * scale
        img_shape_scaled = scale * img_shape
        crop = (img_shape_scaled[0] - img_shape[0]) // 2, (img_shape_scaled[1] - img_shape[1]) // 2
        coords = np.array((-crop[1], -crop[0], -crop[1], -crop[0]))
        #print(coords)
        #print(bboxs_scaled)
        bboxs_scaled = np.add(bboxs_scaled, coords)
        #print(bboxs_scaled)

        if np.all(bboxs_scaled[:, (0, 2)] > crop[1]) and np.all(
                bboxs_scaled[:, (1, 3)] > crop[0]) and np.all(
                    bboxs_scaled[:, (0, 2)] < crop[1] + img_shape[0]) and np.all(
                        bboxs_scaled[:, (1, 3)] < crop[0] + img_shape[0]):
            rescaled_img = rescale(img, scale, anti_aliasing=True, multichannel=True, mode="constant")
            return rescaled_img[int(crop[0]): int(crop[0]) + img_shape[0], int(crop[1]): int(crop[1]) + img_shape[1], :], bboxs_scaled
        else:
            return img, bboxs


class Rotate:
    STD_DEV = 5

    def __call__(self, img, bboxs):
        angle = np.random.randn(1) * self.STD_DEV / 180. * np.pi
        bboxs = self._transform_bboxes(angle, bboxs, np.array(img.shape))
        return rotate(img, angle * 180 / np.pi, resize=False), bboxs

    def _transform_bboxes(self, angle, bboxs, img_shape):
        c_a = np.cos(angle)
        s_a = np.sin(angle)
        center = np.array((img_shape[1] // 2, img_shape[0] // 2))
        matrix = np.matrix([
            [float(c_a), float(-s_a)], [float(s_a), float(c_a)]
        ])
        for box_num in range(bboxs.shape[0]):
            start_point = np.array((bboxs[box_num, 0] - center[0], bboxs[box_num, 1] - center[1]))
            end_point = np.array((bboxs[box_num, 2] - center[0], bboxs[box_num, 3] - center[1]))
            start_point = np.squeeze(np.dot(matrix.T, start_point))
            end_point = np.squeeze(np.dot(matrix.T, end_point))
            bboxs[box_num, :] = np.concatenate([start_point[0, :] + center, end_point[0, :] + center], axis=1)
        # print(bboxs)
        return bboxs


class Normalize:
    def __init__(self, means, stds):
        assert len(means) == 3, "Only three channel images are accepted."
        assert len(stds) == 3
        self._means = means
        self._stds = stds

    def __call__(self, img, bboxs):
        img[:, :, 0] = (img[:, :, 0] - self._means[0]) / self._stds[0]
        img[:, :, 1] = (img[:, :, 1] - self._means[1]) / self._stds[1]
        img[:, :, 2] = (img[:, :, 2] - self._means[2]) / self._stds[2]
        return img, bboxs


if __name__ == "__main__":
    img = cv2.imread("./data/images/Benes_Noc_01_10212_20_06_19$12_56_47.png", cv2.IMREAD_COLOR)
    bbox = np.array((466, 373, 1145, 497))
    from matplotlib import pyplot as plt
    # res = Scale(0.5)
    # img, bbox = res(img, bbox[np.newaxis, :])
    r = Rotate()
    img, bbox = r(img, bbox[np.newaxis, :])
    img = cv2.rectangle(img, (int(bbox[0, 0]), int(bbox[0, 1])), (int(bbox[0, 2]), int(bbox[0, 3])), (255, 0, 0), 2)
    plt.imshow(img)
    plt.show()
