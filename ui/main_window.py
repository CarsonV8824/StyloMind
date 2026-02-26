# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.widgets.button_container import ButtonContainer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.buttons = ButtonContainer()
        self.buttons.go_to_page.connect(self.stack.setCurrentIndex)

        # add pages to stack...