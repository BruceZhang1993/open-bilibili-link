from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel


class QClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, _):
        self.clicked.emit()
