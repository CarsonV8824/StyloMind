# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QWidget
from ui.widgets.button_container import ButtonContainer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.buttons = ButtonContainer()
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.buttons)
        self.main_layout.addWidget(self.stack)
        self.buttons.go_to_page.connect(self.stack.setCurrentIndex)
       
        
        
    
        



        # add pages to stack...
