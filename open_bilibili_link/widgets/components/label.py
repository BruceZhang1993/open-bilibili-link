from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor
from PyQt5.QtWidgets import QLabel


class QClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, _):
        self.clicked.emit()


class KeyframeLabel(QLabel):
    live_status_text = ''

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.live_status_text:
            painter = QPainter(self)
            painter.setPen(Qt.white)
            painter.setFont(QFont('sans-serif', 10))
            painter.fillRect(self.rect(), QBrush(QColor(40, 40, 40, 80)))
            painter.drawText(self.rect().adjusted(5, 0, 0, -5), Qt.AlignLeft | Qt.AlignBottom, self.live_status_text)
