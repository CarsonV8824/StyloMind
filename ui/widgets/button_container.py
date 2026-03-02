# ui/widgets/button_container.py
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt

class ButtonContainer(QWidget):
    go_to_page = Signal(int)  

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setObjectName("button_container")
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout.setContentsMargins(12, 12, 12, 12)
        
        btn1 = QPushButton("Manage Texts")
        btn1.setObjectName("btn_container_btn")
        btn1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  
        btn1.setFixedWidth(btn1.height() // 2)
       
        btn3 = QPushButton("Stats for one Text")
        btn3.setObjectName("btn_container_btn")
        btn3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  
        btn3.setFixedWidth(btn3.height() // 2)

        btn4 = QPushButton("Stats comparing two Texts")
        btn4.setObjectName("btn_container_btn")
        btn4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) 
        btn4.setFixedWidth(btn4.height() // 2)

        btn5 = QPushButton("AI Detection")
        btn5.setObjectName("btn_container_btn")
        btn5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) 
        btn5.setFixedWidth(btn4.height() // 2)

        btn1.clicked.connect(lambda: self.go_to_page.emit(0))
        btn3.clicked.connect(lambda: self.go_to_page.emit(1))
        btn4.clicked.connect(lambda: self.go_to_page.emit(2))
        btn5.clicked.connect(lambda: self.go_to_page.emit(3))

        layout.addWidget(btn1)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
        layout.addWidget(btn5)
