from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QScrollArea, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt
import services.learn as textTraining

from database.database import Database

def _ratio(num: int, den: int) -> float:
    return (num / den) if den else 0.0

class OneTextStatsPage(QWidget):
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

        self.choose_text_for_stats = QComboBox()
        self.load_past_texts()
        self.content_layout.addWidget(self.choose_text_for_stats)

        self.make_graphs = QPushButton("Get Stats")
        self.make_graphs.clicked.connect(self.make_graph)
        self.content_layout.addWidget(self.make_graphs)

        self.figure = None
        self.canvas = None

    def set_text(self, text: tuple[str, str]):
        self.choose_text_for_stats.addItem(text[1], userData=text[0])

    def load_past_texts(self):
        past_text = Database.get_all_text()
        if past_text:
            for entry in past_text:
                self.choose_text_for_stats.addItem(entry[1], userData=entry[2])

    def make_graph(self):
        self._ensure_canvas()
        self.plot_dashboard()

    def _ensure_canvas(self):
        chosen_text = self.choose_text_for_stats.currentData()
        if not chosen_text:
            QMessageBox.warning(self, "popup","No Text choosen")
            return
        if self.figure is not None and self.canvas is not None:
            return

        # Lazy import heavy plotting stack to keep app startup responsive.
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        self.figure = Figure(figsize=(15, 18))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.canvas.setMinimumSize(1200, 1700)
        self.content_layout.addWidget(self.canvas)

    def plot_dashboard(self):
        import numpy as np
        import seaborn as sns

        chosen_text = self.choose_text_for_stats.currentData()
        self.figure.clear()

        if not chosen_text:
            QMessageBox.warning(self, "popup","No Text choosen")
            return

        sentence_data = textTraining.make_text_into_sentences_with_part_of_speech(chosen_text)
        non_empty_sentences = [s for s in sentence_data if s]
        if not non_empty_sentences:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No sentence data available", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
            self.canvas.draw()
            return

        sentence_lengths = []
        avg_token_lengths = []
        stop_word_ratio = []
        punct_ratio = []
        noun_ratio = []
        verb_ratio = []
        passive_flags = []

        flat_non_punct = []
        pos_counts = {"NOUN": 0, "VERB": 0, "ADJ": 0, "ADV": 0, "PRON": 0, "DET": 0}
        tense_counts = {"Past": 0, "Present": 0, "Other": 0}

        for sentence in non_empty_sentences:
            total = len(sentence)
            non_punct = [t for t in sentence if not t["is_punct"]]
            sentence_lengths.append(len(non_punct))
            avg_token_lengths.append(
                np.mean([t["length"] for t in non_punct]) if non_punct else 0.0
            )
            stop_word_ratio.append(
                _ratio(sum(1 for t in non_punct if t["is_stop"]), len(non_punct))
            )
            punct_ratio.append(_ratio(sum(1 for t in sentence if t["is_punct"]), total))
            noun_ratio.append(_ratio(sum(1 for t in non_punct if t["pos"] == "NOUN"), len(non_punct)))
            verb_ratio.append(_ratio(sum(1 for t in non_punct if t["pos"] == "VERB"), len(non_punct)))
            passive_flags.append(
                any(t["dep"] in {"auxpass", "nsubjpass"} for t in sentence)
            )

            for token in sentence:
                if not token["is_punct"]:
                    flat_non_punct.append(token)
                    if token["pos"] in pos_counts:
                        pos_counts[token["pos"]] += 1
                    if token["pos"] in {"AUX", "VERB"}:
                        morph = token["morph"]
                        if "Tense=Past" in morph:
                            tense_counts["Past"] += 1
                        elif "Tense=Pres" in morph:
                            tense_counts["Present"] += 1
                        else:
                            tense_counts["Other"] += 1

        word_lengths = [t["length"] for t in flat_non_punct]
        uppercase_ratio = _ratio(sum(1 for t in flat_non_punct if t["is_upper"]), len(flat_non_punct))
        title_ratio = _ratio(sum(1 for t in flat_non_punct if t["is_title"]), len(flat_non_punct))

        lemmas = [t["lemma"].lower() for t in flat_non_punct if t["lemma"]]
        chunk_size = 120
        lexical_diversity = []
        for i in range(0, len(lemmas), chunk_size):
            chunk = lemmas[i : i + chunk_size]
            if chunk:
                lexical_diversity.append(len(set(chunk)) / len(chunk))

        passive_count = sum(passive_flags)
        active_count = len(passive_flags) - passive_count

        axs = self.figure.subplots(4, 2)

        ax = axs[0, 0]
        sns.histplot(sentence_lengths, bins=12, kde=True, stat="count", ax=ax)
        ax.axvline(np.mean(sentence_lengths), linestyle="--", label=f"Mean: {np.mean(sentence_lengths):.1f}")
        ax.axvline(np.median(sentence_lengths), linestyle="-.", label=f"Median: {np.median(sentence_lengths):.1f}")
        ax.set_title("Sentence Length Distribution")
        ax.set_xlabel("Words per Sentence")
        ax.set_ylabel("Frequency")
        ax.legend()

        ax = axs[0, 1]
        x = np.arange(1, len(sentence_lengths) + 1)
        ax.plot(x, avg_token_lengths, label="Avg token length")
        ax.plot(x, stop_word_ratio, label="% stop words")
        ax.plot(x, punct_ratio, label="% punctuation")
        ax.plot(x, noun_ratio, label="% nouns")
        ax.plot(x, verb_ratio, label="% verbs")
        ax.set_title("Sentence Complexity Over Time")
        ax.set_xlabel("Sentence Index")
        ax.set_ylabel("Ratio / Avg length")
        ax.legend(fontsize=8)

        ax = axs[1, 0]
        ax.bar(list(pos_counts.keys()), list(pos_counts.values()))
        ax.set_title("POS Frequency")
        ax.set_xlabel("Part of Speech")
        ax.set_ylabel("Count")

        ax = axs[1, 1]
        ax.plot(x, noun_ratio, label="Noun Ratio")
        ax.plot(x, verb_ratio, label="Verb Ratio")
        ax.set_title("POS Density Per Sentence")
        ax.set_xlabel("Sentence Index")
        ax.set_ylabel("Ratio")
        ax.legend()

        ax = axs[2, 0]
        if lexical_diversity:
            ax.plot(np.arange(1, len(lexical_diversity) + 1), lexical_diversity)
        ax.set_title("Lexical Diversity Over Chunks")
        ax.set_xlabel(f"Chunk Index ({chunk_size} tokens/chunk)")
        ax.set_ylabel("Unique lemmas / total")

        ax = axs[2, 1]
        if word_lengths:
            sns.histplot(word_lengths, bins=12, kde=True, stat="count", ax=ax)
        ax.set_title("Word Length Distribution")
        ax.set_xlabel("Word Length")
        ax.set_ylabel("Frequency")

        ax = axs[3, 0]
        if len(passive_flags):
            ax.pie([active_count, passive_count], labels=["Active", "Passive"], autopct="%1.1f%%")
        else:
            ax.text(0.5, 0.5, "No sentence data", ha="center", va="center", transform=ax.transAxes)
        ax.set_title("Passive Voice Share")

        ax = axs[3, 1]
        ax.bar(
            ["UPPER", "Title", "Past", "Present", "Other Verb Tense"],
            [
                uppercase_ratio * 100,
                title_ratio * 100,
                tense_counts["Past"],
                tense_counts["Present"],
                tense_counts["Other"],
            ],
        )
        ax.set_title("Capitalization + Verb Tense Distribution")
        ax.set_ylabel("% for Caps / Count for Tense")
        ax.tick_params(axis="x", rotation=20)

        self.figure.tight_layout()
        self.canvas.draw()
