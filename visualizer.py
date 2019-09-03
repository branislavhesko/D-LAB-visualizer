import glob
import os

import cv2
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from tqdm import tqdm

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
matplotlib.use("Qt5Agg")
from matplotlib import pyplot as plt
import smopy

from dataloader import DataLoader


class Visualizer:

    def __init__(self, folder="./data"):
        self._data_loader = DataLoader()
        data_file = glob.glob(os.path.join(folder, "*.txt"))[0]
        video_file = glob.glob(os.path.join(folder, "*.mp4"))[0]
        self._data_loader.load(data_file)
        self.video = self.load_video(video_file)
        self.gps_coords = None
        self.fig = None
        self.map = None

    def calculate_map_coordinates(self):
        self.gps_coords = self._data_loader.gps_on_time()
        longitude = 0.9 * (np.amax(self.gps_coords["GPS_Longitude"].values) - np.amin(self.gps_coords["GPS_Longitude"].values))
        latitude = 1. * (np.amax(self.gps_coords["GPS_Latitude"].values) - np.amin(self.gps_coords["GPS_Latitude"].values))
        # TODO: this is not correct
        lowest_point = (np.amin(self.gps_coords["GPS_Longitude"].values) + 0.1 * longitude, np.amin(
            self.gps_coords["GPS_Latitude"].values))
        print(lowest_point)
        return lowest_point, longitude, latitude

    def load_map(self, lowest_point, longitude, latitude):
        self.fig = plt.figure("GPS", figsize=(20, 8), dpi=300)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        self.map = smopy.Map((lowest_point[1], lowest_point[0], lowest_point[1] + latitude, lowest_point[0] + longitude), z=15)
        gps_in_img_coords = []
        for coord in range(self.gps_coords.shape[0]):
            x, y = self.map.to_pixels(*self.gps_coords[["GPS_Longitude", "GPS_Latitude"]].iloc[coord, :].values[::-1])
            gps_in_img_coords.append((x, y))
        self.gps_coords["longitude_img"] = np.array(gps_in_img_coords)[:, 0]
        self.gps_coords["latitude_img"] = np.array(gps_in_img_coords)[:, 1]

    def load_video(self, video_file):
        video = cv2.VideoCapture(video_file)
        return video

    def on_click(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

    def process_video(self, video_name: str):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video = cv2.VideoWriter(video_name, fourcc, self.video.get(cv2.CAP_PROP_FPS), (
            int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        ret = True
        i=0
        for _ in tqdm(range(int(self.video.get(cv2.CAP_PROP_FRAME_COUNT)))):
            ret, frame = self.video.read()
            i+=1
            if i%100!=0:
                continue
            frame_time = self.video.get(cv2.CAP_PROP_POS_MSEC)
            output = self.process_single_frame(frame, frame_time)
            output_video.write(output)
            if i == 30000:
                break
        output_video.release()

    def process_single_frame(self, frame, frame_time):
        fig = Figure(figsize=(16, 9), dpi=120)
        ax = fig.add_subplot(2, 2, 1)
        ax.imshow(frame)
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.imshow(vis.map.img)
        ax2.plot(vis.gps_coords["longitude_img"], vis.gps_coords["latitude_img"])
        closest_time = np.argmin(np.abs(vis.gps_coords["rec_time"].values - frame_time / 1000))
        ax2.plot(vis.gps_coords["longitude_img"].values[closest_time],
                 vis.gps_coords["latitude_img"].values[closest_time],
                 "xg", markersize=15)
        ax2.legend(["GPS route", "Actual position"])
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.imshow(vis.map.img)
        fig_canvas = FigureCanvas(fig)
        fig_canvas.draw()  # draw the canvas, cache the renderer
        s, (width, height) = fig_canvas.print_to_buffer()
        image = np.frombuffer(fig_canvas.tostring_rgb(), dtype='uint8').reshape(height, width, 3)
        return image


if __name__ == "__main__":
    vis = Visualizer()
    out = vis.calculate_map_coordinates()
    vis.load_map(*out)
    vis.process_video("./out.mp4")
