"""Line numbers and breakpoints
"""

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QPainter, QPalette, \
                        QColor, QBrush, \
                        QTextBlock, QWidget

class LineNumberArea(QWidget):
    BPToggled = pyqtSignal(int, name = 'BPToggled')

    def __init__(self, mainEditor):
        QWidget.__init__(self, mainEditor)
        self.mainEditor = mainEditor
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor('#073642'))
        palette.setColor(QPalette.Text, QColor('#93a1a1'))
        self.setPalette(palette)
        self.setMouseTracking(True)
        self.breakpoints = [ ]


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Window))
        painter.setPen(Qt.black)

        block = self.mainEditor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.mainEditor.blockBoundingGeometry(block).translated(self.mainEditor.contentOffset()).top())
        bottom = top + int(self.mainEditor.blockBoundingRect(block).height())


        boundingRect = self.mainEditor.blockBoundingRect(block)

        bpBrush = QBrush(QColor(250,0,0,128))

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line = blockNumber + 1
                w = self.width() - self.margin
                h = self.mainEditor.fontMetrics().height()
                painter.setPen(Qt.black)
                painter.drawText(0, top, w, h, Qt.AlignRight, str(line))
                if line in self.breakpoints:
                    #paint break point
                    s = min(w, h) - 3
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(bpBrush)
                    painter.drawEllipse((w - s) / 2, top + 1.5 , s, s)

            block = block.next()
            boundingRect = self.mainEditor.blockBoundingRect(block)
            top = bottom
            bottom = top + int(boundingRect.height())
            blockNumber += 1

    @property
    def margin(self):
        return 4

    def width(self):
        digits = max(5, len(str(self.mainEditor.blockCount())))
        return self.margin * 2 + self.mainEditor.fontMetrics().width('9') * digits

    @property
    def fileName(self):
        return self.mainEditor.currentFile

    def mousePressEvent(self, event):
        pos = event.pos()
        if pos.y() > self.mainEditor.fontMetrics().height() * self.mainEditor.blockCount():
            return
        cursor = self.mainEditor.cursorForPosition(pos)
        block = cursor.block()
        if not block.isValid():
            return
        blockNumber = block.blockNumber()
        self.BPToggled.emit(blockNumber + 1)
        #if blockNumber in self.breakpoints:
        #    self.breakpoints.remove(blockNumber)
        #else:
        #    self.breakpoints.append(blockNumber)
        #self.repaint()

    def updateBP(self):
        pass
    def updateArrow(self):
        pass
