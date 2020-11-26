import sys

import cv2
import matplotlib
import numpy as np

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot, ticker
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets

from config import Configuration, CanSignals
from visualizer import Visualizer
from annotator_window import AnnotatorWindow
from checkable_combobox import CheckableComboBox
from video_player import ControlWindow


class MainWindow(QtWidgets.QMainWindow):
    send_fig = QtCore.pyqtSignal(str)

    POSSIBLE_TIME_AXES = {
        "0.1s": 0.1,
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
        "0.1s": 0.1,
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

    def __init__(self, video_file: str):
        super(MainWindow, self).__init__()
        # self.grabKeyboard()
        self.frame_time = 0
        pyplot.grid(True)
        self.main_widget = QtWidgets.QWidget(self)
        self.video_file = video_file
        self.annotator = AnnotatorWindow()
        self.time_interval = self.POSSIBLE_TIME_AXES["5s"]
        self.time_between_frames = self.POSSIBLE_TIMES_BETWEEN_FRAMES["5s"]
        self.fig = Figure(tight_layout=True)
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = [self.fig.add_subplot(2, 2, 3)]
        self.ax4 = [self.fig.add_subplot(2, 2, 4)]
        self.ax1.axis("off")
        self.axes = [self.ax1]
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event', self.on_click)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.visualizer = Visualizer()
        self._video = cv2.VideoCapture(video_file)
        self._video_player = ControlWindow(self, self._video)
        self.dropdown1 = QtWidgets.QComboBox()
        self.dropdown1.addItems(list(self.POSSIBLE_TIME_AXES.keys()))
        self.dropdown1.setCurrentIndex(0)
        self.dropdown2 = QtWidgets.QComboBox()
        self.dropdown2.addItems(list(self.POSSIBLE_TIMES_BETWEEN_FRAMES.keys()))
        self.dropdown2.setCurrentIndex(2)
        self.next_frame_button = QtWidgets.QPushButton("NEXT FRAME")
        self.annotator_button = QtWidgets.QPushButton("ANNOTATE")
        self.annotator_button.setToolTip("runs annotator window")
        self.annotator_button.clicked.connect(self._annotate)
        self.annotator_button.setShortcut("CTRL+A")
        self.next_frame_button.setToolTip("moves to the next frame")
        self.next_frame_button.clicked.connect(self.on_button_forward)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.minimum = 0
        self.slider.setMaximum(self._video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.setValue(self._video.get(cv2.CAP_PROP_POS_FRAMES))
        self.slider.sliderReleased.connect(self.slider_action)

        self.dropdown1.currentIndexChanged.connect(self._dropdown_time_interval_action)
        self.dropdown2.currentIndexChanged.connect(self._dropdown2_time_interval_action)
        self.label = QtWidgets.QLabel("A plot:")

        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.layout.addWidget(QtWidgets.QLabel("Select time axis for signals"), 0, 0)
        self.layout.addWidget(self.dropdown1, 1, 0)
        self.layout.addWidget(QtWidgets.QLabel("Select next frame step"), 0, 1)
        self.layout.addWidget(QtWidgets.QLabel("Move in video"), 0, 2)
        self.video_move = QtWidgets.QPushButton("VIDEO PLAYER")
        self.video_move.clicked.connect(self._video_player_action)
        self.video_move.setShortcut("CTRL+V")
        self.layout.addWidget(self.video_move, 1, 2)
        self.layout.addWidget(self.dropdown2, 1, 1)
        self.layout.addWidget(QtWidgets.QLabel("Synchronization time"), 0, 3)
        self.synchronization_text_field = QtWidgets.QLineEdit("0")
        self.synchronization_text_field.textChanged.connect(self._apply_synchronization_time)
        self.synchronization_text_field.setMaximumWidth(120)
        self._synchronization_time = 0
        self._which_signal_to_plot = CheckableComboBox(self)
        self.layout.addWidget(self._which_signal_to_plot, 2, 2)
        self.layout.addWidget(self.synchronization_text_field, 1, 3)
        self.layout.addWidget(self.next_frame_button, 2, 0, 1, 1)
        self.layout.addWidget(self.annotator_button, 2, 1, 1, 1)
        self.saver_button = QtWidgets.QPushButton("SAVE INTO CSV")
        self.saver_button.clicked.connect(self.saver_button_action)
        self.layout.addWidget(self.saver_button, 2, 3)
        self.layout.addWidget(self.canvas, 3, 0, 1, 3)
        self.layout.addWidget(self.slider, 4, 0, 1, 3)
        self.slider_label = QtWidgets.QLabel(self.get_position_label_text())
        self.slider_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.slider_label2 = QtWidgets.QLabel(self.get_mouse_position(0, 0))
        self.slider_label2.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.slider_label, 5, 1, 1, 1)
        self.layout.addWidget(self.slider_label2, 5, 0, 1, 1)
        out = self.visualizer.calculate_map_coordinates()
        self.visualizer.load_map(*out)
        self.setCentralWidget(self.main_widget)
        for index in range(1, len(CanSignals.SIGNAL_KEYS)):
            self.ax3.append(self.ax3[0].twinx())

        for index in range(1, len(self.visualizer.data_loader.bio_signals.sensor)):
            self.ax4.append(self.ax4[0].twinx())

        for sensor in self.visualizer.data_loader.bio_signals.sensor:
            self._which_signal_to_plot.addItem(sensor)

        self.plots = []
        self._checked_sensors = []

        self.show()
        self.update()

    def saver_button_action(self):
        frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
        biosignals = self.visualizer.data_loader.get_biosignals_in_time_window(
            (frame_time + self._synchronization_time) / 1000, self.time_interval, signal_names=None)
        biosignals = pd.concat([biosignals[0]["rec_time"], pd.concat(biosignals, axis=1).iloc[:, 1::2]], axis=1)
        car_signals = self.visualizer.data_loader.get_car_signals_in_time_window(frame_time / 1000, self.time_interval)
        car_signals = pd.concat([car_signals[0]["rec_time"], pd.concat(car_signals, axis=1).iloc[:, 1::2]], axis=1)
        biosignals.to_csv("biosignals_time_{}s_synchro_{}s.csv".format(
            int(frame_time // 1000), int(self._synchronization_time // 1000)), index=False)
        car_signals.to_csv("car_signals_{}s_synchro_{}s.csv".format(
            int(frame_time // 1000), int(self._synchronization_time // 1000)), index=False)

    def on_click(self, event):
        self.slider_label2.setText(self.get_mouse_position(event.xdata, event.ydata))

    def _video_player_action(self):
        self._video_player.show()

    def _annotate(self):
        frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC) / 1000.
        time_utc = self.visualizer.data_loader.get_time_utc(frame_time)
        self.annotator.run(self.video_file, time_utc)

    def _apply_synchronization_time(self):
        try:
            self._synchronization_time = float(self.synchronization_text_field.text()) * 1000.
            self.update_without_next()
        except ValueError:
            pass

    def _dropdown_time_interval_action(self):
        self.time_interval = self.POSSIBLE_TIME_AXES[self.dropdown1.currentText()]
        self.time_between_frames = self.POSSIBLE_TIMES_BETWEEN_FRAMES[self.dropdown1.currentText()]
        self.dropdown2.setCurrentText(self.dropdown1.currentText())
        self.update_without_next()

    def _dropdown2_time_interval_action(self):
        self.time_interval = self.POSSIBLE_TIME_AXES[self.dropdown2.currentText()]
        self.time_between_frames = self.POSSIBLE_TIMES_BETWEEN_FRAMES[self.dropdown2.currentText()]
        self.dropdown1.setCurrentText(self.dropdown2.currentText())

        self.update_without_next()

    def update_without_next(self):
        self.frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
        self._video.set(cv2.CAP_PROP_POS_MSEC, self.frame_time)
        ret, frame = self._video.read()
        self.process_single_frame(frame[:, :, ::-1], self.frame_time, self.axes)

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

        self.ax2.legend(["GPS route", "Actual position"], loc="upper right")

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
            time = [frame_time / 1000 - self.time_interval,
                    frame_time / 1000 + self.time_interval]
            bio_plots.append(
                self.ax4[index].plot(bio_signal.iloc[:, 0], bio_signal.iloc[:, 1], self.visualizer.COLORS[index])[0])
            self.ax4[index].tick_params(axis="y", colors=self.visualizer.COLORS[index], **tkw)
            self.ax4[index].set_xlim(time[0], time[1])
            xticks = ticker.MaxNLocator(20)
            self.ax4[index].xaxis.set_major_locator(xticks)
        self.ax4[0].set_xlabel("time [s]")
        self.ax4[0].legend(bio_plots, self.visualizer.data_loader.bio_signals.sensor, loc="upper right")

    def _plot_can_signals(self, frame_time):
        [a.clear() for a in self.ax3]
        tkw = dict(size=4, width=1.5)
        plots = []
        signals = self.visualizer.data_loader.get_car_signals_in_time_window(frame_time / 1000, self.time_interval)
        for index, car_signal in enumerate(signals):
            time = [frame_time / 1000 - self.time_interval,
                    frame_time / 1000 + self.time_interval]
            plots.append(self.ax3[index].plot(car_signal.iloc[:, 0], car_signal.iloc[:, 1],
                                              self.visualizer.COLORS[index], linewidth=0.5, mew=0.5)[0])
            self.ax3[index].tick_params(axis='y', colors=self.visualizer.COLORS[index], **tkw)
            self.ax3[index].set_xlim(time[0], time[1])
            xticks = ticker.MaxNLocator(20)
            self.ax3[index].xaxis.set_major_locator(xticks)
        self.ax3[0].set_xlabel("time [s]")
        self.ax3[0].legend(plots, CanSignals.SIGNAL_KEYS, loc="upper right")

    @QtCore.pyqtSlot()
    def on_button_forward(self):
        self.process_video()
        self.slider_label.setText(self.get_position_label_text())
        self.slider.setValue(self._video.get(cv2.CAP_PROP_POS_FRAMES))

    @QtCore.pyqtSlot()
    def on_button_back(self):
        self.process_video(-1)
        self.slider_label.setText(self.get_position_label_text())
        self.slider.setValue(self._video.get(cv2.CAP_PROP_POS_FRAMES))

    @QtCore.pyqtSlot()
    def slider_action(self):
        value = self.slider.value()
        print(value)
        self._video.set(cv2.CAP_PROP_POS_FRAMES, value)
        ret, frame = self._video.read()
        self.frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
        self.process_single_frame(frame[:, :, ::-1], self.frame_time, self.axes)
        self.slider_label.setText(self.get_position_label_text())

    def get_position_label_text(self):
        return "Video position: {} / {}, CAN position: {:.2f}, BIOSIGNAL position: {:.2f}".format(
            self.visualizer.data_loader.format_time_to_hours(self._video.get(cv2.CAP_PROP_POS_MSEC) / 1000),
            self.visualizer.data_loader.format_time_to_hours(self._video.get(
                cv2.CAP_PROP_FRAME_COUNT) / self._video.get(cv2.CAP_PROP_FPS)),
            self.frame_time / 1000., (self.frame_time + self._synchronization_time) / 1000.)

    def update(self):

        colors = ["b", "r", "g", "y", "k", "c"]
        self.process_video()
        self.slider_label.repaint()

    def process_video(self, forward=1):
        actual = self._video.get(cv2.CAP_PROP_POS_FRAMES)
        self._video.set(cv2.CAP_PROP_POS_FRAMES,
                        actual + forward * self.time_between_frames * self._video.get(cv2.CAP_PROP_FPS))
        ret, frame = self._video.read()
        self.frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
        self.process_single_frame(frame[:, :, ::-1], self.frame_time, self.axes)

    def get_mouse_position(self, x, y):
        return "MOUSE position, X: {:.3f}, Y: {:.3f}.".format(x, y)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        print(a0)
        if a0.key() == QtCore.Qt.Key_A:
            print("Annotator pressed!")
            self._annotate()

        elif a0.key() == QtCore.Qt.Key_Right:
            print("Right key pressed!")
            self.on_button_forward()

        elif a0.key() == QtCore.Qt.Key_Left:
            print("Left key pressed!")
            self.on_button_back()

        elif a0.key() == QtCore.Qt.Key_Return:
            self.synchronization_text_field.clearFocus()
        super().keyPressEvent(a0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow(Configuration.VIDEO_FILE)
    sys.exit(app.exec_())
