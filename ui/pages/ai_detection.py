from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QScrollArea, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt
import services.learn as textTraining

from database.database import Database

import pandas as pd
import numpy as np

from services.machine_learn import test_text_for_ai

class AiDetectionPage(QWidget):

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.text_choose_list_box = QComboBox()
        self.content_layout.addWidget(self.text_choose_list_box)

        self.confirm_button = QPushButton("Find the percentage of your text written in an AI style")
        self.confirm_button.clicked.connect(self.get_data_of_ai_detection_in_paper)
        self.content_layout.addWidget(self.confirm_button)

        self.load_past_texts()
    
    def set_text(self, text: tuple[str, str]):
        self.text_choose_list_box.addItem(text[1], userData=text[0])

    def load_past_texts(self):
        past_text = Database.get_all_text()
        if past_text:
            print("text added in ai detect")
            for entry in past_text:
                self.text_choose_list_box.addItem(entry[1], userData=entry[2])
        else:
            print("no text in database from ai detect")

    def update_text(self, text: list[tuple[str, str]]):
        self.text_choose_list_box.clear()
        if text:
            for entry in text:
                self.text_choose_list_box.addItem(entry[1], userData=entry[2])

    def get_data_of_ai_detection_in_paper(self):
        text = self.text_choose_list_box.currentData()
        if not text:
            QMessageBox.warning(self, "popup","No Text choosen")
            return
        data = test_text_for_ai(text)
        sum_list = np.mean([value for value in data.values()])

        ai_percent = round(sum_list, 2)
        human_percent = round(1 - ai_percent, 2)
        print(ai_percent, human_percent)

        for sent, score in data.items():
            if score == 1.0:
                pass
                #print(sent)
        
