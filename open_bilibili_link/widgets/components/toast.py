import asyncio

from PySide6.QtCore import QTimerEvent, Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QMessageBox, QWidget, QApplication


class Toast(QMessageBox):
    delay: int = 0
    current_time: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setContentsMargins(0, 0, 0, 0)
        # Set centered
        if self.window:
            x = int((self.parent().width() - self.width()) / 2)
            y = int((self.parent().height() - self.height()) / 2)
            self.setGeometry(x, y, self.width(), self.height())

    def showEvent(self, _) -> None:
        self.current_time = 0
        if self.delay > 0:
            self.startTimer(1000)

    def timerEvent(self, _) -> None:
        self.current_time += 1
        if self.current_time >= self.delay:
            self.done(0)

    @classmethod
    def toast(cls, parent, text):
        toast = cls(parent)
        toast.setText(text)
        toast.delay = 3
        toast.show()
