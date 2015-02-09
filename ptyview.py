""" This module implements a PTY """
import os
from PyQt4 import QtCore
from PyQt4 import QtGui

class PtyView(QtCore.QThread):
    """ A class that wraps PTY read/display"""
    data_ready = QtCore.pyqtSignal(QtCore.QString)
    def __init__(self, text_widget):
        super(PtyView, self).__init__()
        self.text_widget = text_widget
        self.master, self.slave = os.openpty()
        self.slave_name = os.ttyname(self.slave)
        self.file_obj = os.fdopen(self.master, 'r')
        QtCore.QThread.__init__(self)
        self.start()
        self.data_ready.connect(self.handle_data)

    def handle_data(self, line):
        """ slot for receiving data"""
        self.text_widget.append(line)
        self.text_widget.moveCursor(QtGui.QTextCursor.End)

    def get_file_path(self):
        """ overrided """
        return self.slave_name

    def run(self):
        """ runner """
        while True:
            line = self.file_obj.readline()
            self.data_ready.emit(line)
