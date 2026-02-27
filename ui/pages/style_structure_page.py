from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QComboBox, QMessageBox
from PySide6.QtCore import Qt
import services.learn as textTraining

class StyleStructurePage(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.text_label = QLabel("on data manager page")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.text_label)

        self.first_text_box = QComboBox()
        self.main_layout.addWidget(self.first_text_box)

        self.second_text_box = QComboBox()
        self.main_layout.addWidget(self.second_text_box)

        self.compare = QPushButton("Compare Texts")
        self.main_layout.addWidget(self.compare)
        self.compare.clicked.connect(self.find_struct_and_style)

        self.structure_label = QLabel()
        self.main_layout.addWidget(self.structure_label)

        self.style_label = QLabel()
        self.main_layout.addWidget(self.style_label)

    def set_text(self, text: list[str, str]):

        self.first_text_box.addItem(text[1], userData=text[0])
        self.second_text_box.addItem(text[1], userData=text[0])

    def find_struct_and_style(self):
        first_text = self.first_text_box.currentData()
        second_text = self.second_text_box.currentData()

        if not first_text or not second_text:
            QMessageBox.warning(self, "popup", "Texts not choosen")
            return
        print("from find_struct_and_style: ", first_text[:10])
        print("from find_struct_and_style: ", second_text[:10])

        percentage_structure = textTraining.structure_similarity(first_text, second_text)
        percentage_style = textTraining.style_similarity(first_text, second_text)
        print(percentage_structure)
        print(percentage_style)
        self.structure_label.setText(f"Simularity in Structure: {round(percentage_structure * 100, 2)}%")
        self.style_label.setText(f"Simularity in Style: {round(percentage_style * 100, 2)}%")
