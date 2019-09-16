import cv2
import sys
from tqdm import tqdm

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
        self.ax1 = self.fig.add_subplot(111)
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
        self.dropdown1.addItems(["sex", "time", "smoker"])
        self.dropdown2 = QtWidgets.QComboBox()
        self.dropdown2.addItems(["sex", "time", "smoker", "day"])
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
        self.layout.addWidget(QtWidgets.QLabel("Select category for subplots"), 0, 0)
        self.layout.addWidget(self.dropdown1, 1, 0)
        self.layout.addWidget(QtWidgets.QLabel("Select category for markers"), 0, 1)
        self.layout.addWidget(self.dropdown2, 1, 1)
        self.layout.addWidget(self.next_frame_button, 2, 0, 1, 2)

        self.layout.addWidget(self.canvas, 3, 0, 1, 2)
        self.layout.addWidget(self.slider, 4, 0, 1, 2)
        self.slider_label = QtWidgets.QLabel(self.get_position_label_text())
        self.slider_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.layout.addWidget(self.slider_label, 5, 1)
        self.video = self.process_video()
        out = self.visualizer.calculate_map_coordinates()
        self.visualizer.load_map(*out)
        self.setCentralWidget(self.main_widget)
        self.show()
        self.update()

    @QtCore.pyqtSlot()
    def on_button(self):
        self.ax1.clear()
        self.ax1.imshow(next(self.video))

        self.fig.canvas.draw_idle()
        self.slider_label.setText(self.get_position_label_text())

    @QtCore.pyqtSlot()
    def slider_action(self):
        value = self.slider.value()
        print(value)
        self._video.set(cv2.CAP_PROP_POS_FRAMES, value)
        ret, frame = self._video.read()
        output = self.visualizer.process_single_frame(frame[:, :, ::-1], self._video.get(cv2.CAP_PROP_POS_MSEC), self.axes)
        self.ax1.clear()
        self.ax1.imshow(output)
        self.fig.canvas.draw_idle()
        self.slider_label.setText(self.get_position_label_text())

    def get_position_label_text(self):
        return "Video position: {} / {}".format(
            self.visualizer.data_loader.format_time_to_hours(self._video.get(cv2.CAP_PROP_POS_MSEC) / 1000),
            self.visualizer.data_loader.format_time_to_hours(self._video.get(
                cv2.CAP_PROP_FRAME_COUNT) / self._video.get(cv2.CAP_PROP_FPS)))

    def update(self):

        colors=["b", "r", "g", "y", "k", "c"]
        self.ax1.clear()
        self.ax1.imshow(next(self.video))
        self.ax1.axis("off")
        self.fig.canvas.draw_idle()
        self.slider_label.repaint()


    def process_video(self):
        for _ in tqdm(range(int(self._video.get(cv2.CAP_PROP_FRAME_COUNT)))):
            ret, frame = self._video.read()
            frame_time = self._video.get(cv2.CAP_PROP_POS_MSEC)
            if _ % 100 != 0:
                continue
            output = self.visualizer.process_single_frame(frame[:, :, ::-1], frame_time, self.axes)
            yield output


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
