import glob
import os

import cv2
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from tqdm import tqdm

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import pyplot as plt
import smopy

from dataloader import DataLoader


class Visualizer:
    COLORS = ["red", "green", "blue", "brown", "darkviolet", "skyblue", "black", "orange", "silver", "fuchsia"]

    def __init__(self, folder="./data"):
        self.data_loader = DataLoader()
        self.data_loader.load()
        self.gps_coords = None
        self.fig = None
        self.map = None

    def calculate_map_coordinates(self):
        self.gps_coords = self.data_loader.gps_on_time()
        longitude = 0.9 * (np.amax(self.gps_coords["GPS_Longitude"].values) - np.amin(
            self.gps_coords["GPS_Longitude"].values))
        latitude = 1. * (np.amax(self.gps_coords["GPS_Latitude"].values) - np.amin(
            self.gps_coords["GPS_Latitude"].values))
        # TODO: this is not correct
        lowest_point = (np.amin(self.gps_coords["GPS_Longitude"].values) + 0.1 * longitude, np.amin(
            self.gps_coords["GPS_Latitude"].values))
        print(lowest_point)
        return lowest_point, longitude, latitude

    def load_map(self, lowest_point, longitude, latitude):
        self.fig = plt.figure("GPS", figsize=(20, 8), dpi=300)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        self.map = smopy.Map((lowest_point[1], lowest_point[0], lowest_point[1] + latitude,
                              lowest_point[0] + longitude), z=15)
        gps_in_img_coords = []
        for coord in range(self.gps_coords.shape[0]):
            x, y = self.map.to_pixels(*self.gps_coords[["GPS_Longitude", "GPS_Latitude"]].iloc[coord, :].values[::-1])
            gps_in_img_coords.append((x, y))
        self.gps_coords["longitude_img"] = np.array(gps_in_img_coords)[:, 0]
        self.gps_coords["latitude_img"] = np.array(gps_in_img_coords)[:, 1]

    def on_click(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

    def process_single_frame(self, frame, frame_time, axes):
        fig = Figure(figsize=(16, 9), dpi=60)
        ax = fig.add_subplot(2, 2, 1)
        ax.imshow(frame)
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.imshow(self.map.img)
        ax2.plot(self.gps_coords["longitude_img"], self.gps_coords["latitude_img"])
        closest_time = np.argmin(np.abs(self.gps_coords["rec_time"].values - frame_time / 1000))
        ax2.plot(self.gps_coords["longitude_img"].values[closest_time],
                 self.gps_coords["latitude_img"].values[closest_time],
                 "xr", markersize=21, mew=2)
        ax2.text(self.gps_coords["longitude_img"].values[closest_time] + 20,
                 self.gps_coords["latitude_img"].values[closest_time] - 10,
                 "Actual position", color="red")
        ax2.legend(["GPS route", "Actual position"])
        ax3 = fig.add_subplot(2, 2, 3)
        ax_temp = [ax3]
        tkw = dict(size=4, width=1.5)
        signals = self.data_loader.get_car_signals_in_time_window(frame_time / 1000, 30)
        for index, car_signal in enumerate(signals):
            ax_temp[-1].plot(car_signal.iloc[:, 1], self.COLORS[index])
            ax_temp[-1].tick_params(axis='y', colors=self.COLORS[index], **tkw)
            if index < len(signals) - 1:
                ax_temp.append(ax_temp[0].twinx())

        fig.subplots_adjust(bottom=0.05, top=0.95, left=0.05, right=0.95)
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
