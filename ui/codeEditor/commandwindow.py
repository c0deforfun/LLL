""" Command window for input commands and display outputs from debugger """
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QPlainTextEdit, QTextCursor
import logging

class CommandWindow(QPlainTextEdit):
    """ This class accepts text and user inputs """
    PROMPT = '>'
    commandEntered = pyqtSignal(str, name='commandEntered')

    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)
        self.cursorPositionChanged.connect(self.cursorChanged)

    def append(self, text):
        """ output text to the window"""
        cursor = self.textCursor()
        if not cursor.atBlockStart():
            cursor.movePosition(QTextCursor.End)
        self.textCursor().insertText(text + '\n' + self.PROMPT)
        self.ensureCursorVisible()

    def cursorChanged(self):
        """ make pass text read-only """
        cursor = self.textCursor()
        if cursor.blockNumber() + 1 == self.blockCount() and not cursor.atBlockStart():
            self.setReadOnly(False)
        else:
            self.setReadOnly(True)

    def keyPressEvent(self, event):
        """ handle if special key is pressed (enter, up, down, tab, etc) """
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            logging.info("TODO: history")
            return
        if event.key() == Qt.Key_Tab:
            logging.info("TODO: completion")
            return
        if event.key() == Qt.Key_Backspace and self.textCursor().columnNumber() == 1:
            return

        if event.key() == Qt.Key_Return:
            cmd = self.textCursor().block().text()
            cmd = cmd[1:]
            # move to the next line
            QPlainTextEdit.keyPressEvent(self, event)
            self.commandEntered.emit(str(cmd))
            return
        QPlainTextEdit.keyPressEvent(self, event)

