""" for showing message on status bar"""
from PyQt4.QtGui import QTreeView, QStandardItem, QStandardItemModel, QHeaderView

import logging, logging.handlers


class FrameInfoViewer(QTreeView):
    """ Customized status bar  """
    def __init__(self, parent):
        super(QTreeView, self).__init__(parent)
        self.setAutoScroll(True)
        self.source_files = {}
        self.focus_signal = None
        self.header().setResizeMode(QHeaderView.ResizeToContents)

    def set_focus_signal(self, signal):
        self.focus_signal = signal

    @staticmethod
    def get_empty_model():
        frame_data = QStandardItemModel()
        frame_data.setColumnCount(2)
        frame_data.setHorizontalHeaderLabels(['',''])
        return frame_data

    def clear(self):
        frame_data = self.get_empty_model()
        self.setModel(frame_data)
        self.setAlternatingRowColors(True)
        self.resizeColumnToContents(1)
        self.expandToDepth(1)


    def show_frame_info(self, process):
        if not self.isVisible:
            return
        frame_data = self.get_empty_model()
        root = frame_data.invisibleRootItem()
        self.source_files.clear()
        if process is None or not process.is_alive:
            self.clear()
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
            for frame in thread.frames:
                # first show the frame on the top of call stack.
                frame_idx = '#%d: ' % frame.idx
                frame_info = ''
                selectable = False
                if frame.name:
                    frame_idx += frame.name
                    args = ','.join(map(str, frame.args))
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
                col_idx.setEditable(False)
                col_idx.setSelectable(selectable)

                col_info = QStandardItem(frame_info)
                col_info.setEditable(False)
                col_info.setSelectable(selectable)

                thread_row.appendRow([col_idx, col_info])

        self.setModel(frame_data)
        self.expandToDepth(1)

    def mousePressEvent(self, event):
        idx = self.indexAt(event.pos());
        if idx.isValid() and self.focus_signal:
            model = idx.model()
            idx = idx.sibling(idx.row(), 0)
            if idx.isValid():
                item = model.itemFromIndex(idx)
                if item and item.isSelectable():
                    if item in self.source_files:
                        file_info = self.source_files[item]
                        self.focus_signal.emit(file_info.GetFileSpec().fullpath,
                                               file_info.GetLine())

                    else:
                        logging.ERROR('frame cannot find associated source file')

        QTreeView.mousePressEvent(self, event)
