from PyQt5.QtCore import QTimerEvent
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import QMessageBox, QWidget


class Toast(QMessageBox):
    delay: int = 0
    current_time: int = 0

    def showEvent(self, _) -> None:
        self.current_time = 0
        if self.delay > 0:
            self.startTimer(1000)

    def timerEvent(self, _) -> None:
        self.current_time += 1
        if self.current_time >= self.delay:
            self.done(0)
