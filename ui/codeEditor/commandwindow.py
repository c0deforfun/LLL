from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QPlainTextEdit, QTextCursor
import logging                       

class CommandWindow(QPlainTextEdit):
    PROMPT = '>'
    commandEntered = pyqtSignal(str, name = 'commandEntered')

    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)
        self.cursorPositionChanged.connect(self.cursorChanged)

    def append(self, text):
        cursor = self.textCursor()
        if not cursor.atBlockStart():
            cursor.movePosition(QTextCursor.End)
        self.textCursor().insertText(text + '\n' + self.PROMPT)
        self.ensureCursorVisible()
    
    def cursorChanged(self):
        cursor = self.textCursor()
        if cursor.blockNumber() + 1 == self.blockCount() and not cursor.atBlockStart():
            self.setReadOnly(False)
        else:
            self.setReadOnly(True)

    def keyPressEvent(self, event):
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
            QPlainTextEdit.keyPressEvent(self, event) #move the next line
            self.commandEntered.emit(str(cmd))
            return
        QPlainTextEdit.keyPressEvent(self, event)

