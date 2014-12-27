"""Line numbers and breakpoints
"""

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QPainter, QPalette, \
                        QColor, QBrush, QWidget

class LineNumberArea(QWidget):
    """ The left pane for line number and toggling breakpoints
    """
    BPToggled = pyqtSignal(int, name='BPToggled')
    MARGIN = 4

    def __init__(self, main_editor):
        QWidget.__init__(self, main_editor)
        self.main_editor = main_editor
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor('#073642'))
        palette.setColor(QPalette.Text, QColor('#93a1a1'))
        self.setPalette(palette)
        self.setMouseTracking(True)
        self.breakpoints = []

    def paintEvent(self, event):
        """ paint a circle for each bp """
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Window))
        painter.setPen(Qt.black)

        block = self.main_editor.firstVisibleBlock()
        block_num = block.blockNumber()
        top = int(self.main_editor.blockBoundingGeometry(block).translated(
            self.main_editor.contentOffset()).top())
        bottom = top + int(self.main_editor.blockBoundingRect(block).height())

        bounding_rect = self.main_editor.blockBoundingRect(block)

        bp_brush = QBrush(QColor(250, 0, 0, 128))

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line = block_num + 1
                width = self.width() - self.MARGIN
                height = self.main_editor.fontMetrics().height()
                painter.setPen(Qt.black)
                painter.drawText(0, top, width, height, Qt.AlignRight, str(line))
                if line in self.breakpoints:
                    # paint break point
                    diameter = min(width, height) - 3
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(bp_brush)
                    painter.drawEllipse((width - diameter) / 2, top + 1.5, diameter, diameter)

            block = block.next()
            bounding_rect = self.main_editor.blockBoundingRect(block)
            top = bottom
            bottom = top + int(bounding_rect.height())
            block_num += 1

    def width(self):
        """ sets the width of itself """
        digits = max(5, len(str(self.main_editor.blockCount())))
        return self.MARGIN * 2 + self.main_editor.fontMetrics().width('9') * digits

    @property
    def filename(self):
        """
        :return:filename associated with the editor
        """
        return self.main_editor.source_file

    def mousePressEvent(self, event):
        """ when mouse pressed, toggle the corresponding BP """
        pos = event.pos()
        if pos.y() > self.main_editor.fontMetrics().height() * self.main_editor.blockCount():
            return
        cursor = self.main_editor.cursorForPosition(pos)
        block = cursor.block()
        if not block.isValid():
            return
        block_num = block.blockNumber()
        self.BPToggled.emit(block_num + 1)
