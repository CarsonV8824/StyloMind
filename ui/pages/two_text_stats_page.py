from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QScrollArea, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt
import services.learn as textTraining

from database.database import Database

class TwoTextStatsPage(QWidget):
    def __init__(self):
        super().__init__()