import datetime
import sys

from PyQt5 import QtCore, QtGui, QtWidgets


class AnnotatorWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Annotation window"
        self.top = 250
        self.left = 300
        self.width = 870
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.main_widget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.layout.maximumSize()
        self.button = QtWidgets.QPushButton("ANNOTATE")
        self.button.setToolTip("Click to annotate.")
        self.button.clicked.connect(self.click_button)
        self.text_field = QtWidgets.QTextEdit("write your annotation here!")
        self.layout.addWidget(self.button, 0, 0)
        self.layout.addWidget(self.text_field, 1, 0)
        self.text = ""
        self.setCentralWidget(self.main_widget)
        self.video_file = None
        self.time = None
        self.hide()
        self.update()

    def click_button(self):
        self.text = self.text_field.toPlainText()
        self.text = self.text.replace("\n", " ")

        with open("annotation.txt", "a") as f:
            output = "\t".join([self.video_file,
                                self.from_seconds_to_datetime(self.time / 1000.),
                                str(self.time), self.text])
            f.write(output + "\n")
        self.text = ""
        self.releaseKeyboard()
        self.hide()

    def run(self, video_file, time):
        self.grabKeyboard()
        self.text = ""
        self.video_file = video_file
        self.time = time
        print(time)
        self.show()

    @staticmethod
    def from_seconds_to_datetime(seconds_from_epoch):
        return datetime.datetime.fromtimestamp(seconds_from_epoch).strftime("%m_%d_%Y-%H_%M_%S")

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        print(a0)
        if a0.key() == QtCore.Qt.Key_F1:
            self.click_button()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AnnotatorWindow()
    sys.exit(app.exec_())