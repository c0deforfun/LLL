""" for showing source file tree"""
from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QFileSystemModel, QHeaderView, QItemSelectionModel
from PyQt4.QtCore import QDir
import logging, os

from ui.UISourceFileTreeWidget import Ui_SourceFileTreeWidget

class SourceFileTreeWidget(QWidget):
    """ Config window"""
    def __init__(self, parent):
        super(SourceFileTreeWidget, self).__init__(parent)
        self.ui = Ui_SourceFileTreeWidget()
        self.ui.setupUi(self)
        self.file_model = QFileSystemModel()
        #self.file_model.setFilter(QDir.AllEntries | QDir.NoDot)
        self.set_filter()
        self.ui.tree.setModel(self.file_model)
        self.ui.tree.resizeColumnToContents(0)
        self.ui.custom_root.setText(QDir.currentPath())
        self.set_root()

        header = self.ui.tree.header()
        header.setResizeMode(QHeaderView.ResizeToContents)
        #header.setStretchLastSection(True)
        #header.setSortIndicator(0, Qt.AscendingOrder)
        #header.setSortIndicatorShown(True)
        #header.setClickable(True)
        self.connect(self.ui.tree, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.open_file)
        self.connect(self.ui.ok_filter, QtCore.SIGNAL('clicked()'), self.set_filter)
        self.connect(self.ui.custom_filter, QtCore.SIGNAL('returnPressed()'), self.set_filter)
        self.connect(self.ui.ok_root, QtCore.SIGNAL('clicked()'), self.set_root)
        self.connect(self.ui.custom_root, QtCore.SIGNAL('returnPressed()'), self.set_root)
        self.open_file_signal = None

    def set_open_file_signal(self, signal):
        """ callback to signal file opening """
        self.open_file_signal = signal

    def set_root(self, root=None, use_common_prefix=True):
        """ set the root path of the widget """
        curr = str(self.ui.custom_root.text())
        if not root:
            use_common_prefix = False # input text box will override it.
            root = self.ui.custom_root.text()
        else:
            self.ui.custom_root.setText(root)
        idx = self.file_model.index(root)
        self.ui.tree.setExpanded(idx, True)
        if use_common_prefix and curr == os.path.commonprefix([root, curr]):
            return

        idx = self.file_model.setRootPath(root)
        if not idx.isValid():
            logging.warn('Invalid path')
            return
        self.ui.tree.setRootIndex(idx)
        self.ui.tree.setExpanded(idx, True)

    def set_filter(self):
        """ set filter by extension """
        filters = str(self.ui.custom_filter.text()).split(';')
        self.file_model.setNameFilters(filters)
        self.file_model.setNameFilterDisables(False)

    def open_file(self, idx):
        """ emit file opening signal """
        if self.file_model.isDir(idx):
            return
        fullpath = self.file_model.filePath(idx)
        if self.open_file_signal:
            self.open_file_signal.emit(str(fullpath), 0)

    def set_file_selected(self, tab_idx):
        """ slot to associate the file in active tab """
        filename = self.sender().tabToolTip(tab_idx)
        idx = self.file_model.index(filename)
        if idx.isValid():
            self.ui.tree.selectionModel().select(idx, QItemSelectionModel.ClearAndSelect)

