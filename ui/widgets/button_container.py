# ui/widgets/button_container.py
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class ButtonContainer(QWidget):
    go_to_page = Signal(int)  # sends page index

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        btn1 = QPushButton("Upload your Text")
        btn2 = QPushButton("Style and Structure")
        btn3 = QPushButton("Stats of a Text")

        btn1.clicked.connect(lambda: self.go_to_page.emit(0))
        btn2.clicked.connect(lambda: self.go_to_page.emit(1))
        btn3.clicked.connect(lambda: self.go_to_page.emit(2))

        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
