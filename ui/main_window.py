# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QWidget
from ui.widgets.button_container import ButtonContainer

from ui.pages.upload_page import UploadPage

from ui.pages.style_structure_page import StyleStructurePage

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

        # put pages here

        self.upload_page = UploadPage()
        self.stack.addWidget(self.upload_page)

        self.data_manager_page = StyleStructurePage()

        self.stack.addWidget(self.data_manager_page)

        # signals

        self.upload_page.send_text.connect(self.data_manager_page.set_text)
        self.buttons.go_to_page.connect(self.stack.setCurrentIndex)
