import platform

from PyQt4.QtCore import QRect, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QAction, QApplication, QColor, QBrush, \
                        QDialog, QFont, \
                        QKeySequence, QPainter, QPen, QPalette, \
                        QPlainTextEdit, \
                        QPrintDialog, QTextCharFormat, QTextCursor, \
                        QTextBlock, QTextEdit, QTextFormat

from ui.codeEditor.sideareas import LineNumberArea
from ui.codeEditor.parser import Highlighter

class CodeEditor(QPlainTextEdit):

    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)

        self.lineNumberArea = LineNumberArea(self)
        self.lineNumberArea.setObjectName('lineNumberArea') # Used for slot

        #TODO: color theme
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor('#fdf6e3'))
        palette.setColor(QPalette.Text, QColor('#002b36'))
        self.setPalette(palette)

        self.highlighter = Highlighter(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.currentFile = ''

    def openSourceFile(self, filePath):
        self.currentFile = filePath
        txt = open(self.currentFile).read()
        self.setPlainText(txt)
        self.highlighter.highlight(filePath)

    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberArea.width(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberArea.width(), cr.height()))

    #@pyqtSlot(str, int, name = 'on_eventListener_FocuseLine')
    def focuseLine(self, lineNo):
        lineNo -= 1
        cursor = QTextCursor(self.document().findBlockByLineNumber(lineNo))
        cursor.clearSelection()
        highlight = QTextEdit.ExtraSelection()
        highlight.cursor = cursor
        highlight.format.setProperty(QTextFormat.FullWidthSelection, True)
        highlight.format.setBackground(QBrush(QColor("#657b83")))
        self.setExtraSelections([highlight])
