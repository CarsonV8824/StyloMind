# ui/widgets/button_container.py
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class ButtonContainer(QWidget):
    go_to_page = Signal(int)  # sends page index

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        btn1 = QPushButton("Go to Page 1")
        btn2 = QPushButton("Go to Page 2")

        btn1.clicked.connect(lambda: self.go_to_page.emit(0))
        btn2.clicked.connect(lambda: self.go_to_page.emit(1))

        layout.addWidget(btn1)
        layout.addWidget(btn2)
