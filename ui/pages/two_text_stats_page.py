from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QScrollArea, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt
import services.graph_NLP as textTraining

from database.database import Database

import pandas as pd

class TwoTextStatsPage(QWidget):
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

        self.first_text = QComboBox()
        self.content_layout.addWidget(self.first_text)

        self.second_text = QComboBox()
        self.content_layout.addWidget(self.second_text)

        self.load_past_texts()

        self.make_graphs = QPushButton("Get Stats")
        self.make_graphs.clicked.connect(self.make_graph)
        self.content_layout.addWidget(self.make_graphs)

        self.figure = None
        self.canvas = None

    def load_past_texts(self):
        past_text = Database.get_all_text()
        if past_text:
            for entry in past_text:
                self.first_text.addItem(entry[1], userData=entry[2])
                self.second_text.addItem(entry[1], userData=entry[2])

    def set_text(self, text: list[str]):
        if not text or len(text) < 2:
            return
        content = text[0]
        label = text[1]
        if not isinstance(content, str) or not isinstance(label, str):
            return
        self.first_text.addItem(label, userData=content)
        self.second_text.addItem(label, userData=content)

    def update_text(self, text: list[tuple[str, str]]):
        self.first_text.clear()
        self.second_text.clear()
        if text:
            for entry in text:
                self.first_text.addItem(entry[1], userData=entry[2])
                self.second_text.addItem(entry[1], userData=entry[2])

    def make_graph(self):
        if not self._ensure_canvas():
            return
        self.plot_dashboard()

    def _ensure_canvas(self):
        if self.figure is not None and self.canvas is not None:
            return True

        # Lazy import heavy plotting stack to keep app startup responsive.
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        self.figure = Figure(figsize=(10, 6), constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(900, 600)
        self.content_layout.addWidget(self.canvas)
        return True

    def plot_dashboard(self):
        import seaborn as sns

        first_chosen_text = self.first_text.currentData()
        second_chosen_text = self.second_text.currentData()

        if not isinstance(first_chosen_text, str):
            first_chosen_text = self.first_text.currentText()
        if not isinstance(second_chosen_text, str):
            second_chosen_text = self.second_text.currentText()

        if not first_chosen_text or not second_chosen_text:
            QMessageBox.warning(self, "popup", "No text chosen.")
            return

        self.figure.clear()

        # Percentage stuff

        percentage_structure = textTraining.structure_similarity(first_chosen_text, second_chosen_text)
        percentage_style = textTraining.style_similarity(first_chosen_text, second_chosen_text)

        percentage_structure *= 100
        percentage_style *= 100

        # other stats stuff

        first_text_sentences = textTraining.make_text_into_sentences_with_part_of_speech(first_chosen_text)
        second_text_sentences = textTraining.make_text_into_sentences_with_part_of_speech(second_chosen_text)

        first_text_sentences = [sentence for sentence in first_text_sentences if sentence]
        second_text_sentences = [sentence for sentence in second_text_sentences if sentence]

        percentage_df = pd.DataFrame(
            {
                "Metric": ["Structure", "Style"],
                "Similarity": [percentage_structure, percentage_style],
            }
        )

        ax = self.figure.subplots(1, 1)
        sns.barplot(data=percentage_df, x="Metric", y="Similarity", ax=ax)
        ax.set_title("Text Similarity Comparison")
        ax.set_xlabel("")
        ax.set_ylabel("Similarity (%)")
        ax.bar_label(ax.containers[0], fmt="%.2f", padding=3)

        ax.set_ylim(0, 100)

        self.canvas.draw()
