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
        self._tab_comp_handler = None

    def set_tab_comp_handler(self, func):
        """ set signal for tab completion """
        self._tab_comp_handler = func

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
        """ append command to history """
        if cmd in self.history:
            self.history.remove(cmd)
        self.history.append(cmd)

    def clear_current_line(self):
        """ clear the input on current line """
        if self.isReadOnly():
            return
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self.PROMPT)

    def tab_complete(self, cmd):
        """ complete on tab pressed """
        if cmd:
            self._tab_comp_handler(cmd)

    def execute_command(self, cmd):
        """ execute command when enter is pressed """
        if not cmd and self.history_idx:
            cmd = self.history[-1]
        if cmd:
            # move to the next line
            self.commandEntered.emit(cmd)
            logging.debug('executing cmd:' + cmd)
            self.add_cmd_to_history(cmd)
            self.history_idx = len(self.history)
            self.append('')
        else:
            self.clear_current_line()

    def get_command(self):
        cmd = self.textCursor().block().text()
        cmd = str(cmd)
        cmd = cmd[1:]
        cmd = cmd.strip()
        return cmd

    def on_escape(self, event):
        self.clear_current_line()

    def default_key_event(self, event):
        QPlainTextEdit.keyPressEvent(self, event)

    def on_up_down(self, event):
        key_up = event.key() == Qt.Key_Up
        key_down = event.key() == Qt.Key_Down
        if (self.history_idx == 0 and key_up) or \
                (self.history_idx == len(self.history) -1 and key_down):
                    return
        if key_up:
            self.history_idx -= 1          
        else:
            self.history_idx += 1
        cmd = self.history[self.history_idx]
        self.clear_current_line()
        self.textCursor().insertText(cmd)

    def on_backspace(self, event):
        """ do back deletion if not the first char """
        if self.textCursor().columnNumber() != 1:
            self.default_key_event(event)
            
    def on_tab(self, event):
        cmd = self.get_command()
        self.tab_complete(cmd)

    def on_return(self, event):
        cmd = self.get_command()
        self.execute_command(cmd)

    def keyPressEvent(self, event):
        """ handle if special key is pressed (enter, up, down, tab, etc) """
        {
                Qt.Key_Escape: self.on_escape,
                Qt.Key_Up: self.on_up_down,
                Qt.Key_Down: self.on_up_down,
                Qt.Key_Backspace: self.on_backspace,
                Qt.Key_Tab: self.on_tab,
                Qt.Key_Return: self.on_return
        }.get(event.key(), self.default_key_event)(event)
