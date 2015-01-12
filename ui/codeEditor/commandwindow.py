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
        self.history = []
        self.history_idx = 0

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

    def add_cmd_to_history(self, cmd):
        if cmd in self.history:
            self.history.remove(cmd)
        self.history.append(cmd)

    def clear_current_line(self):
        if self.isReadOnly():
            return
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self.PROMPT)

    def keyPressEvent(self, event):
        """ handle if special key is pressed (enter, up, down, tab, etc) """
        if event.key() == Qt.Key_Escape:
            self.clear_current_line()
            return

        key_up = event.key() == Qt.Key_Up
        key_down = event.key() == Qt.Key_Down
        if key_up or key_down:
            if self.history_idx == 0 and key_up:
                return
            if self.history_idx == len(self.history) -1 and key_down:
                return
            if key_up:
                self.history_idx -= 1
            if key_down:
                self.history_idx += 1
            cmd = self.history[self.history_idx]
            self.clear_current_line()
            self.textCursor().insertText(cmd)
            return
        #reset history idx
        self.history_idx = len(self.history)
        if event.key() == Qt.Key_Tab:
            logging.info("TODO: completion")
            return
        if event.key() == Qt.Key_Backspace and self.textCursor().columnNumber() == 1:
            return

        if event.key() == Qt.Key_Return:
            cmd = self.textCursor().block().text()
            cmd = str(cmd)
            cmd = cmd[1:]
            cmd = cmd.strip()
            if not cmd and self.history_idx:
                cmd = self.history[-1]
            if not cmd:
                self.clear_current_line()
                return
            # move to the next line
            QPlainTextEdit.keyPressEvent(self, event)

            self.commandEntered.emit(cmd)
            self.add_cmd_to_history(cmd)
            return
        QPlainTextEdit.keyPressEvent(self, event)

