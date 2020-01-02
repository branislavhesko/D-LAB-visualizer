import cv2
import sys
from tqdm import tqdm

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvas, FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import pyplot, ticker
from PyQt5 import QtCore, QtGui, QtWidgets
from visualizer import Visualizer
from annotator_window import AnnotatorWindow
from checkable_combobox import CheckableComboBox


class MainWindow(QtWidgets.QMainWindow):
    send_fig = QtCore.pyqtSignal(str)

    POSSIBLE_TIME_AXES = {
        "0.5s": 0.5,
        "1s": 1,
        "2s": 2,
        "5s": 5,
        "10s": 10,
        "30s": 30,
        "1min": 60,
        "3min": 180,
        "10min": 600
    }

    POSSIBLE_TIMES_BETWEEN_FRAMES = {
        "1s": 1,
        "3s": 3,
        "10s": 10,
        "30s": 30
    }

    def __init__(self, video_file: str):
        super(MainWindow, self).__init__()
        pyplot.grid(True)
        self.main_widget = QtWidgets.QWidget(self)
        self.video_file = video_file
        self.annotator = AnnotatorWindow()
        self.time_interval = self.POSSIBLE_TIME_AXES["1min"]
        self.time_between_frames = self.POSSIBLE_TIMES_BETWEEN_FRAMES["3s"]
        self.fig = Figure(tight_layout=True)
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = [self.fig.add_subplot(2, 2, 3)]
        self.ax4 = [self.fig.add_subplot(2, 2, 4)]
        self.ax1.axis("off")
        self.axes = [self.ax1]
        self.canvas = FigureCanvas(self.fig)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.visualizer = Visualizer()
        self._video = cv2.VideoCapture(video_file)
        self.dropdown1 = QtWidgets.QComboBox()
        self.dropdown1.addItems(list(self.POSSIBLE_TIME_AXES.keys()))
        self.dropdown2 = QtWidgets.QComboBox()
        self.dropdown2.addItems(list(self.POSSIBLE_TIMES_BETWEEN_FRAMES.keys()))
        self.dropdown2.setCurrentIndex(2)
        self.next_frame_button = QtWidgets.QPushButton("NEXT FRAME")
        self.annotator_button = QtWidgets.QPushButton("ANNOTATE")
        self.annotator_button.setToolTip("runs annotator window")
        self.annotator_button.clicked.connect(self._annotate)
        self.next_frame_button.setToolTip("moves to the next frame")
        self.next_frame_button.clicked.connect(self.on_button)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.minimum = 0
        self.slider.setMaximum(self._video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.setValue(self._video.get(cv2.CAP_PROP_POS_FRAMES))
        self.slider.sliderReleased.connect(self.slider_action)

        self.dropdown1.currentIndexChanged.connect(self._dropdown_time_interval_action)
        self.dropdown2.currentIndexChanged.connect(self._update)
        self.label = QtWidgets.QLabel("A plot:")

        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.layout.addWidget(QtWidgets.QLabel("Select time axis for signals"), 0, 0)
        self.layout.addWidget(self.dropdown1, 1, 0)
        self.layout.addWidget(QtWidgets.QLabel("Select next frame step"), 0, 1)
        self.layout.addWidget(self.dropdown2, 1, 1)
        self.layout.addWidget(QtWidgets.QLabel("Synchronization time"), 0, 2)
        self.synchronization_text_field = QtWidgets.QLineEdit("0")
        self.synchronization_text_field.textChanged.connect(self._apply_synchronization_time)
        self.synchronization_text_field.setMaximumWidth(120)
        self._synchronization_time = 0
        self._which_signal_to_plot = CheckableComboBox()

        self.layout.addWidget(self._which_signal_to_plot, 2, 2)
        self.layout.addWidget(self.synchronization_text_field, 1, 2)
        self.layout.addWidget(self.next_frame_button, 2, 0, 1, 1)
        self.layout.addWidget(self.annotator_button, 2, 1, 1, 1)

        self.layout.addWidget(self.canvas, 3, 0, 1, 3)
        self.layout.addWidget(self.slider, 4, 0, 1, 3)
        self.slider_label = QtWidgets.QLabel(self.get_position_label_text())
        self.slider_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.layout.addWidget(self.slider_label, 5, 1)
        out = self.visualizer.calculate_map_coordinates()
        self.visualizer.load_map(*out)
        self.setCentralWidget(self.main_widget)
        for index in range(1, len(self.visualizer.data_loader.SIGNAL_KEYS)):
            self.ax3.append(self.ax3[0].twinx())

        for index in range(1, len(self.visualizer.data_loader.bio_signals.sensor)):
            self.ax4.append(self.ax4[0].twinx())

        for sensor in self.visualizer.data_loader.bio_signals.sensor:
            self._which_signal_to_plot.addItem(sensor)

        self.plots = []
        self._checked_sensors = []

        self.show()
        self.update()

    def _annotate(self):
        frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC) / 1000.
        time_utc = self.visualizer.data_loader.get_time_utc(frame_time)
        self.annotator.run(self.video_file, time_utc)

    def _apply_synchronization_time(self):
        try:
            self._synchronization_time = float(self.synchronization_text_field.text()) * 1000.
            self._update()
        except ValueError:
            pass

    def _dropdown_time_interval_action(self):
        self.time_interval = self.POSSIBLE_TIME_AXES[self.dropdown1.currentText()]
        self._update()

    def _update(self):
        frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
        self._video.set(cv2.CAP_PROP_POS_MSEC, frame_time)
        ret, frame = self._video.read()
        self.process_single_frame(frame[:, :, ::-1], frame_time, self.axes)

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
            self.plots.append(self.ax2.plot(self.visualizer.gps_coords["longitude_img"],
                                            self.visualizer.gps_coords["latitude_img"])[0])
            closest_time = np.argmin(np.abs(self.visualizer.gps_coords["rec_time"].values - frame_time / 1000))
            self.plots.append(self.ax2.plot(self.visualizer.gps_coords["longitude_img"].values[closest_time],
                     self.visualizer.gps_coords["latitude_img"].values[closest_time],
                     "xr", markersize=21, mew=2)[0])

        self.ax2.legend(["GPS route", "Actual position"])

        self._plot_can_signals(frame_time)
        self._plot_biosignals(frame_time + self._synchronization_time)

        self.fig.canvas.draw_idle()

    def _plot_biosignals(self, frame_time):
        tkw = dict(size=4, width=1.5)

        [a.clear() for a in self.ax4]
        for i in range(len(self.visualizer.data_loader.bio_signals.sensor)):
            item = self._which_signal_to_plot.model().item(i, 0)
            if item.checkState() == QtCore.Qt.Checked and not item.text() in self._checked_sensors:
                self._checked_sensors.append(item.text())
            elif item.checkState() == QtCore.Qt.Unchecked:
                if item.text() in self._checked_sensors:
                    self._checked_sensors.remove(item.text())
        bio_plots = []
        bio_signals = self.visualizer.data_loader.get_biosignals_in_time_window(
            frame_time / 1000, self.time_interval, self._checked_sensors)
        for index, bio_signal in enumerate(bio_signals):
            time = np.linspace(frame_time / 1000 - self.time_interval,
                               frame_time / 1000 + self.time_interval, len(bio_signal))
            bio_plots.append(self.ax4[index].plot(time, bio_signal.iloc[:, 1], self.visualizer.COLORS[index])[0])
            self.ax4[index].tick_params(axis="y", colors=self.visualizer.COLORS[index],  **tkw)
            xticks = ticker.MaxNLocator(20)
            self.ax4[index].xaxis.set_major_locator(xticks)
        self.ax4[0].set_xlabel("time [s]")
        self.ax4[0].legend(bio_plots, self.visualizer.data_loader.bio_signals.sensor)

    def _plot_can_signals(self, frame_time):
        [a.clear() for a in self.ax3]
        tkw = dict(size=4, width=1.5)
        plots = []
        signals = self.visualizer.data_loader.get_car_signals_in_time_window(frame_time / 1000, self.time_interval)
        for index, car_signal in enumerate(signals):
            time = np.linspace(frame_time / 1000 - self.time_interval,
                               frame_time / 1000 + self.time_interval, len(car_signal))
            plots.append(self.ax3[index].plot(time, car_signal.iloc[:, 1],
                                              self.visualizer.COLORS[index], linewidth=0.5, mew=0.5)[0])
            self.ax3[index].tick_params(axis='y', colors=self.visualizer.COLORS[index], **tkw)
            xticks = ticker.MaxNLocator(20)
            self.ax3[index].xaxis.set_major_locator(xticks)
        self.ax3[0].set_xlabel("time [s]")
        self.ax3[0].legend(plots, self.visualizer.data_loader.SIGNAL_KEYS)

    @QtCore.pyqtSlot()
    def on_button(self):
        self.process_video()
        self.slider_label.setText(self.get_position_label_text())
        self.slider.setValue(self._video.get(cv2.CAP_PROP_POS_FRAMES))

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
        self._video.set(cv2.CAP_PROP_POS_FRAMES,
                        actual + self.time_between_frames * self._video.get(cv2.CAP_PROP_FPS))
        ret, frame = self._video.read()
        frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
        self.process_single_frame(frame[:, :, ::-1], frame_time, self.axes)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    import glob
    win = MainWindow(glob.glob("./data/*.mp4")[0])
    sys.exit(app.exec_())
