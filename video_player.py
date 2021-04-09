import sys
import scipy.io as sio
from PyQt5 import QtGui, QtCore, QtWidgets, Qt
import cv2


class VideoCapture(QtWidgets.QWidget):
    def __init__(self, filename, parent, cap):
        super().__init__()
        self.cap = cap
        self.video_frame = QtWidgets.QLabel()
        self.parent = parent
        parent.layout.addWidget(self.video_frame)
        parent.slider.setMaximum(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        parent.slider.valueChanged.connect(self.sliderMove)
        self._started = False

    def nextFrameSlot(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def sliderMove(self):
        value = int(self.parent.slider.value() - 1)
        value = value if value > 0 else 1
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)
        self.nextFrameSlot()

    def start(self):
        if self._started:
            self._started = False
            self.timer.stop()
            return
        self._started = True
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000//30)

    def pause(self):
        if not self._started:
            return
        self._started = False
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QtWidgets.QWidget, self).deleteLater()


class VideoDisplayWidget(QtWidgets.QWidget):
    def __init__(self,parent):
        super(VideoDisplayWidget, self).__init__(parent)

        self.layout = QtWidgets.QFormLayout(self)

        self.startButton = QtWidgets.QPushButton('Play', parent)
        self.startButton.clicked.connect(parent.startCapture)
        self.startButton.setShortcut(QtCore.Qt.Key_Space)
        self.startButton.setFixedWidth(50)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.layout.addRow(self.startButton)
        self.layout.addRow(self.slider)
        self.setLayout(self.layout)


class ControlWindow(QtWidgets.QMainWindow):
    def __init__(self, parent, cap):
        super(ControlWindow, self).__init__()
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle("Video Player")
        self.cap = cap
        self.capture = None
        self._parent = parent

        self.matPosFileName = None
        self.videoFileName = None
        self.positionData = None
        self.updatedPositionData  = {'red_x':[], 'red_y':[], 'green_x':[], 'green_y': [], 'distance': []}
        self.updatedMatPosFileName = None


        self.quitAction = QtWidgets.QAction("&Exit", self)
        self.quitAction.setShortcut("Ctrl+Q")
        self.quitAction.setStatusTip('Close The App')
        self.quitAction.triggered.connect(self.closeApplication)

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.quitAction)
        self.videoDisplayWidget = VideoDisplayWidget(self)
        self.setCentralWidget(self.videoDisplayWidget)

    def startCapture(self):
        self.grabKeyboard()
        if not self.capture:
            self.capture = VideoCapture(self.videoFileName, self.videoDisplayWidget, self.cap)
        self.capture.start()

    def endCapture(self):
        self.releaseKeyboard()
        self.capture.deleteLater()
        self.capture = None

    def loadVideoFile(self):
        try:
            self.videoFileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Select .h264 Video File')
            self.isVideoFileLoaded = True
        except:
            print("Please select a .h264 file")

    def closeApplication(self):
        self.releaseKeyboard()
        self._parent.update_without_next()
        self.hide()
        # choice = QtWidgets.QMessageBox.question(self, 'Message','Do you really want to exit?',
        #                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # if choice == QtWidgets.QMessageBox.Yes:
        #     print("Closing....")
        #     sys.exit()
        # else:
        #     pass

    @property
    def actual_position(self):
        return int(self.capture.cap.get(cv2.CAP_PROP_POS_FRAMES))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ControlWindow()
    window.show()
    sys.exit(app.exec_())