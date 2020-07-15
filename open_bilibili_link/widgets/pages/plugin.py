from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton


class PluginPage(QFrame):
    btn1: QPushButton

    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.btn1 = QPushButton('Goto home')
        self.btn1.clicked.connect(lambda: self.context.goto('obl://home'))
        layout.addWidget(self.btn1)
        self.setLayout(layout)
