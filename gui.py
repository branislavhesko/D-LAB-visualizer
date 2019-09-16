import cv2
import sys
from tqdm import tqdm

import numpy as np
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvas, FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets
from visualizer import Visualizer


tips = sns.load_dataset("tips")


class MainWindow(QtWidgets.QMainWindow):
    send_fig = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_widget = QtWidgets.QWidget(self)

        self.fig = Figure(tight_layout=True)
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = [self.fig.add_subplot(2, 2, 3)]
        self.ax4 = self.fig.add_subplot(2, 2, 4)
        self.ax1.axis("off")
        self.axes=[self.ax1]
        self.canvas = FigureCanvas(self.fig)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, 
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.visualizer = Visualizer()
        self._video = cv2.VideoCapture("./data/michalrerucha_3. Recording 7242019 41055 PM_Dikablis "
                                       "Glasses 3_Scene Cam_Original_Eye Tracking Video.mp4")
        self.dropdown1 = QtWidgets.QComboBox()
        self.dropdown1.addItems(["30s", "1min", "3min"])
        self.dropdown2 = QtWidgets.QComboBox()
        self.dropdown2.addItems(["3s", "10s", "30s"])
        self.dropdown2.setCurrentIndex(2)
        self.next_frame_button = QtWidgets.QPushButton("NEXT FRAME")
        self.next_frame_button.setToolTip("moves to the next frame")
        self.next_frame_button.clicked.connect(self.on_button)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.minimum = 0
        self.slider.setMaximum(self._video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.setValue(self._video.get(cv2.CAP_PROP_POS_FRAMES))
        self.slider.sliderReleased.connect(self.slider_action)

        self.dropdown1.currentIndexChanged.connect(self.update)
        self.dropdown2.currentIndexChanged.connect(self.update)
        self.label = QtWidgets.QLabel("A plot:")

        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.layout.addWidget(QtWidgets.QLabel("Select time axis for signals"), 0, 0)
        self.layout.addWidget(self.dropdown1, 1, 0)
        self.layout.addWidget(QtWidgets.QLabel("Select next frame step"), 0, 1)
        self.layout.addWidget(self.dropdown2, 1, 1)
        self.layout.addWidget(self.next_frame_button, 2, 0, 1, 2)

        self.layout.addWidget(self.canvas, 3, 0, 1, 2)
        self.layout.addWidget(self.slider, 4, 0, 1, 2)
        self.slider_label = QtWidgets.QLabel(self.get_position_label_text())
        self.slider_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.layout.addWidget(self.slider_label, 5, 1)
        out = self.visualizer.calculate_map_coordinates()
        self.visualizer.load_map(*out)
        self.setCentralWidget(self.main_widget)
        for index in range(1, len(self.visualizer.data_loader.SIGNAL_KEYS)):
            self.ax3.append(self.ax3[0].twinx())
        self.plots = []
        self.show()
        self.update()

    def process_single_frame(self, frame, frame_time, axes):
        if len(self.plots):
            self.plots[0].set_data(frame)
            self.plots[1].set_data(self.visualizer.map.img)
            self.plots[2].set_data(
                self.visualizer.gps_coords["longitude_img"], self.visualizer.gps_coords["latitude_img"])
            closest_time = np.argmin(np.abs(self.visualizer.gps_coords["rec_time"].values - frame_time / 1000))
            self.plots[3].set_data(self.visualizer.gps_coords["longitude_img"].values[closest_time],
                                            self.visualizer.gps_coords["latitude_img"].values[closest_time])

        else:
            self.plots.append(self.ax1.imshow(frame))
            self.ax2.clear()
            self.plots.append(self.ax2.imshow(self.visualizer.map.img))
            self.plots.append(self.ax2.plot(self.visualizer.gps_coords["longitude_img"], self.visualizer.gps_coords["latitude_img"])[0])
            closest_time = np.argmin(np.abs(self.visualizer.gps_coords["rec_time"].values - frame_time / 1000))
            self.plots.append(self.ax2.plot(self.visualizer.gps_coords["longitude_img"].values[closest_time],
                     self.visualizer.gps_coords["latitude_img"].values[closest_time],
                     "xr", markersize=21, mew=2)[0])

        self.ax2.legend(["GPS route", "Actual position"])

        [a.clear() for a in self.ax3]
        tkw = dict(size=4, width=1.5)
        plots = []
        signals = self.visualizer.data_loader.get_car_signals_in_time_window(frame_time / 1000, 30)
        for index, car_signal in enumerate(signals):
            time = np.linspace(frame_time / 1000 - 30, frame_time / 1000 + 30, len(car_signal))
            plots.append(self.ax3[index].plot(time, car_signal.iloc[:, 1], self.visualizer.COLORS[index])[0])
            self.ax3[index].tick_params(axis='y', colors=self.visualizer.COLORS[index], **tkw)
        self.ax3[0].set_xlabel("time [s]")
        self.ax3[0].legend(plots, self.visualizer.data_loader.SIGNAL_KEYS)

        self.fig.canvas.draw_idle()

    @QtCore.pyqtSlot()
    def on_button(self):
        self.process_video()
        self.slider_label.setText(self.get_position_label_text())

    @QtCore.pyqtSlot()
    def slider_action(self):
        value = self.slider.value()
        print(value)
        self._video.set(cv2.CAP_PROP_POS_FRAMES, value)
        ret, frame = self._video.read()
        self.process_single_frame(frame[:, :, ::-1], self._video.get(cv2.CAP_PROP_POS_MSEC), self.axes)
        self.slider_label.setText(self.get_position_label_text())

    def get_position_label_text(self):
        return "Video position: {} / {}".format(
            self.visualizer.data_loader.format_time_to_hours(self._video.get(cv2.CAP_PROP_POS_MSEC) / 1000),
            self.visualizer.data_loader.format_time_to_hours(self._video.get(
                cv2.CAP_PROP_FRAME_COUNT) / self._video.get(cv2.CAP_PROP_FPS)))

    def update(self):

        colors=["b", "r", "g", "y", "k", "c"]
        self.process_video()
        self.slider_label.repaint()

    def process_video(self):
        actual = self._video.get(cv2.CAP_PROP_POS_FRAMES)
        self._video.set(cv2.CAP_PROP_POS_FRAMES, actual + 100)
        ret, frame = self._video.read()
        frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
        self.process_single_frame(frame[:, :, ::-1], frame_time, self.axes)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
