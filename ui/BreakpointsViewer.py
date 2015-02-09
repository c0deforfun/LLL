""" for showing breakpoints"""
from PyQt4.QtGui import QTreeView, QStandardItem, QStandardItemModel, QHeaderView
from lldb import SBBreakpoint
import logging

class BreakpointsViewer(QTreeView):
    """ showing bps  """
    def __init__(self, parent):
        super(QTreeView, self).__init__(parent)
        self.setAutoScroll(True)
        self.source_files = {}
        self.focus_signal = None
        self.header().setResizeMode(QHeaderView.ResizeToContents)
        self._show_args = None
        self.bp_data = QStandardItemModel()
        self.setModel(self.bp_data)
        self.setAlternatingRowColors(True)

    def set_focus_signal(self, signal):
        """ set callback to focus source file line"""
        self.focus_signal = signal

    def clear(self):
        """ clear the widget"""
        self.bp_data.clear()
        self.bp_data.setColumnCount(2)
        self.bp_data.setHorizontalHeaderLabels(['', ''])

    def update_bp_info(self, target):
        """ update breakpoint info """
        self.clear()
        root = self.bp_data.invisibleRootItem()
        for breakpoint in target.breakpoint_iter():
            if not breakpoint.IsValid() or breakpoint.IsInternal():
                continue
            bp_item = QStandardItem(str(breakpoint.id))
            bp_row =[bp_item, QStandardItem(str(breakpoint.GetHitCount())), 
                       QStandardItem(str(breakpoint.GetIgnoreCount())), QStandardItem(str(breakpoint.GetCondition()))]
            for loc in breakpoint:
                loc_row = [QStandardItem(str(loc.GetID())), QStandardItem(str(loc.GetAddress().GetLineEntry()))]
                bp_item.appendRow(loc_row)
            root.appendRow(bp_row)
        self.expandToDepth(1)

    def mousePressEvent(self, event):
        """ overrided """
        idx = self.indexAt(event.pos())
        if idx.isValid() and self.focus_signal:
            model = idx.model()
            idx = idx.sibling(idx.row(), 0)
            if idx.isValid():
                item = model.itemFromIndex(idx)
                if item and item.isSelectable():
                    if item in self.source_files:
                        file_info = self.source_files[item]
                        if self.focus_signal:
                            self.focus_signal.emit(file_info.GetFileSpec().fullpath,
                                                   file_info.GetLine())
                        self.frame_changed.emit(self.frames[item])

                    else:
                        logging.error('frame cannot find associated source file')

        QTreeView.mousePressEvent(self, event)
