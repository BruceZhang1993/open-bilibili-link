from PySide6.QtCore import Signal as pyqtSignal, Qt
from PySide6.QtGui import QPainter, QFont, QBrush, QColor, QMouseEvent
from PySide6.QtWidgets import QLabel


class QClickableLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent, QLabel)

    def mouseReleaseEvent(self, event):
        self.clicked.emit(event, self)


class KeyframeLabel(QLabel):
    live_status_text = ''
    live_online = '...'

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.live_status_text:
            painter = QPainter(self)
            painter.setPen(Qt.white)
            painter.setFont(QFont('sans-serif', 10))
            painter.fillRect(self.rect(), QBrush(QColor(40, 40, 40, 80)))
            painter.drawText(self.rect().adjusted(5, 0, -5, -5), Qt.AlignLeft | Qt.AlignBottom, self.live_status_text)
            painter.drawText(self.rect().adjusted(5, 0, -5, -5), Qt.AlignRight | Qt.AlignBottom, str(self.live_online))
