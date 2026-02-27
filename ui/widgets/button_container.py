# ui/widgets/button_container.py
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class ButtonContainer(QWidget):
    go_to_page = Signal(int)  

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setObjectName("button_container")
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout.setContentsMargins(12, 12, 12, 12)
        btn1 = QPushButton("Upload your Text")
        btn2 = QPushButton("Style and Structure")
        btn3 = QPushButton("Stats for one Text")
        btn4 = QPushButton("Stats comparing two Texts")

        btn1.clicked.connect(lambda: self.go_to_page.emit(0))
        btn2.clicked.connect(lambda: self.go_to_page.emit(1))
        btn3.clicked.connect(lambda: self.go_to_page.emit(2))
        btn4.clicked.connect(lambda: self.go_to_page.emit(3))

        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
