import os
from PyQt4 import QtCore
from PyQt4 import QtGui

class PtyView(QtCore.QThread):
    """ A class that wraps PTY read/display"""
    data_ready = QtCore.pyqtSignal(QtCore.QString)
    def __init__(self, textWidget):
        super(PtyView, self).__init__()
        self.textWidget = textWidget
        self.master, self.slave = os.openpty()
        self.slave_name = os.ttyname(self.slave)
        self.file_obj = os.fdopen(self.master, 'r')
        QtCore.QThread.__init__(self)
        self.start()
        self.data_ready.connect(self.handle_data)

    #@QtCore.pyqtSlot(str)
    def handle_data(self, line):
        self.textWidget.append(line)
        self.textWidget.moveCursor(QtGui.QTextCursor.End)

    def get_file_path(self):
        return self.slave_name

    def run(self):
        while True:
            line = self.file_obj.readline()
            self.data_ready.emit(line)
