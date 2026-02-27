from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QFileDialog

class UploadPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.text_label = QLabel("on upload page")
        self.main_layout.addWidget(self.text_label)

        self.test_button = QPushButton()
        self.test_button.clicked.connect(self.open_dialog)
        self.main_layout.addWidget(self.test_button)

    def open_dialog(self):
        # Returns (file_path, selected_filter)
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Python Files (*.py)"
        )
        if file_path:
            print(f"Selected file: {file_path}")