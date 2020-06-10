from PyQt5 import QtCore, QtGui, QtWidgets


class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self._par = parent

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            print("Unchecked {}".format(item.text()))
        else:
            item.setCheckState(QtCore.Qt.Checked)
            print("Checked {}".format(item.text()))
        self._par.update_without_next()
