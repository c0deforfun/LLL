""" for showing message on status bar"""
from PyQt4.QtGui import QTreeView, QStandardItem, QStandardItemModel, QHeaderView
from PyQt4.QtCore import pyqtSignal
from lldb import SBFrame
import logging, logging.handlers


class FrameInfoViewer(QTreeView):
    """ Customized status bar  """
    frame_changed = pyqtSignal(SBFrame)
    def __init__(self, parent):
        super(QTreeView, self).__init__(parent)
        self.setAutoScroll(True)
        self.source_files = {}
        self.focus_signal = None
        self.header().setResizeMode(QHeaderView.ResizeToContents)
        self._show_args = None
        self.frame_data = QStandardItemModel()
        self.setModel(self.frame_data)
        self.setAlternatingRowColors(True)
        self.top_frame = None
        self.frames = {}

    def set_focus_signal(self, signal):
        """ set callback to focus source file line"""
        self.focus_signal = signal

    def clear(self):
        """ clear the widget"""
        self.frame_data.clear()
        self.frame_data.setColumnCount(2)
        self.frame_data.setHorizontalHeaderLabels(['', ''])

    def show_frame_info(self, process):
        """ show the frame info """
        if not self.isVisible:
            return
        #TODO: no update if top frame is the same
        self.clear()
        root = self.frame_data.invisibleRootItem()
        self.source_files.clear()
        self.frames.clear()

        if process is None or not process.is_alive:
            return

        #if process.num_of_threads == 1:
        for thread in process:
            thread_name = thread.GetName()
            if not thread_name:
                thread_name = '[No Thread]'
            thread_row = QStandardItem(thread_name)
            thread_row.setEditable(False)
            thread_row.setSelectable(False)
            dummy = QStandardItem('')
            dummy.setEditable(False)
            dummy.setSelectable(False)
            root.appendRow([thread_row, dummy])
            if len(thread.frames):
                self.top_frame = thread.frames[0]
                self.frame_changed.emit(self.top_frame)
            for frame in thread.frames:
                # first show the frame on the top of call stack.
                frame_idx = '#%d: ' % frame.idx
                frame_info = ''
                selectable = False
                if frame.name:
                    frame_idx += frame.name
                    if self._show_args.isChecked():
                        args = ','.join([str(x) for x in frame.args])
                        frame_info += ' (%s)' % args
                line = frame.line_entry
                if line:
                    file_info = ' at %s:%d' % (str(line.GetFileSpec()), line.GetLine())
                    frame_info += file_info
                    selectable = True
                else:
                    frame_info += str(frame.module.GetFileSpec())
                if frame.is_inlined:
                    frame_info += ' (inlined)'
                col_idx = QStandardItem(frame_idx)
                self.source_files[col_idx] = line
                self.frames[col_idx] = frame
                col_idx.setEditable(False)
                col_idx.setSelectable(selectable)

                col_info = QStandardItem(frame_info)
                col_info.setEditable(False)
                col_info.setSelectable(selectable)

                thread_row.appendRow([col_idx, col_info])

        self.expandToDepth(1)

    def frame_up(self):
        """ set frame to one level up """
        pass

    def frame_down(self):
        """ set frame to one level down """
        pass

    def set_show_args(self, widget):
        """ set the checkbox of showing func args"""
        self._show_args = widget

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
