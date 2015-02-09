""" the widget for source code and side area"""
from PyQt4 import QtCore
from PyQt4.QtCore import QRect
from PyQt4.QtGui import QAction, QColor, QBrush, \
                        QDialog, QFont, QIcon, \
                        QKeySequence, QPainter, QPen, QPalette, \
                        QPlainTextEdit, QKeySequence, QAction, \
                        QPrintDialog, QTextCharFormat, QTextCursor, \
                        QTextEdit, QTextFormat

from ui.codeEditor.sideareas import LineNumberArea
from ui.codeEditor.parser import Highlighter
import os

class CodeEditor(QPlainTextEdit):
    """ the main widget for displaying source code"""

    def __init__(self, tabWidget=None):
        QPlainTextEdit.__init__(self)

        self.line_number_area = LineNumberArea(self)
        self.line_number_area.setObjectName('lineNumberArea') # Used for slot

        #TODO: color theme
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor('#fdf6e3'))
        palette.setColor(QPalette.Text, QColor('#002b36'))
        self.setPalette(palette)

        self.highlighter = Highlighter(self)

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.source_file = ''
        self.modificationChanged.connect(self.modified)
        self.tabs = tabWidget
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.Save)
        self.connect(save_action, QtCore.SIGNAL('triggered()'), self.save)
        self.addAction(save_action)


    def open_source_file(self, filename):
        """open and show source file"""
        self.source_file = filename
        if os.access(filename, os.R_OK):
            with open(self.source_file, 'r') as f:
                txt = f.read()
                self.setPlainText(txt)
                self.highlighter.highlight(filename)
                self.document().setModified(False)
            if not os.access(filename, os.W_OK):
                self.setReadOnly(True)
                if self.tabs:
                    idx = self.tabs.indexOf(self)
                    self.tabs.setTabIcon(idx, QIcon(":/icons/icons/locked.png"))

    def save(self):
        """ save changes of source file"""
        if os.access(self.source_file, os.W_OK):
            with open(self.source_file, 'w') as f:
                f.write(self.toPlainText())
                self.document().setModified(False)

    def _update_line_number_area_width(self):
        """ change line number area width based on total lines"""
        self.setViewportMargins(self.line_number_area.width(), 0, 0, 0)

    def _update_line_number_area(self, rect, pos_y):
        """ update line number area"""
        if pos_y:
            self.line_number_area.scroll(0, pos_y)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

    def resizeEvent(self, event):
        """ overriding"""
        QPlainTextEdit.resizeEvent(self, event)
        rect = self.contentsRect()
        self.line_number_area.setGeometry(QRect(rect.left(), rect.top(),
                                                self.line_number_area.width(), rect.height()))

    def focus_line(self, line_no):
        """ highlight the line"""
        line_no -= 1
        cursor = QTextCursor(self.document().findBlockByLineNumber(line_no))
        cursor.clearSelection()
        highlight = QTextEdit.ExtraSelection()
        highlight.cursor = cursor
        highlight.format.setProperty(QTextFormat.FullWidthSelection, True)
        highlight.format.setBackground(QBrush(QColor("#657b83")))
        self.setExtraSelections([highlight])
        self.setTextCursor(cursor)

    def modified(self, is_modified):
        """ override """
        if not self.source_file or not self.tabs:
            return
        idx = self.tabs.indexOf(self)
        filename = os.path.basename(self.source_file)
        if is_modified:
            self.tabs.setTabText(idx, filename + '*')
        else:
            self.tabs.setTabText(idx, filename)
