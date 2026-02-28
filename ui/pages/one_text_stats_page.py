from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QScrollArea, QSizePolicy, QMessageBox, QDialog, QLabel, QFileDialog
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

    def update_text(self, text: list[tuple[str, str]]):
        self.choose_text_for_stats.clear()
        if text:
            for entry in text:
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

        self.figure = Figure(figsize=(15, 18), constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(1400, 1800)
        self.content_layout.addWidget(self.canvas)

    def plot_dashboard(self):
        import numpy as np
        import seaborn as sns

        chosen_text = self.choose_text_for_stats.currentData()
        try:
            self.figure.clear()
        except AttributeError:
            print("error clearing")

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
        pov_counts = {"1st":0, "2nd": 0, "3rd":0}

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
                    match token["1st_2nd_3rd"]:
                        case ["1"]: pov_counts["1st"] += 1
                        case ["2"]: pov_counts["2nd"] += 1
                        case ["3"]: pov_counts["3rd"] += 1
                        case _:pass
        print(pov_counts)
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

        pov_chunk_size = 20
        pov_over_time = {"1st": [], "2nd": [], "3rd": []}

        for i in range(0, len(non_empty_sentences), pov_chunk_size):
            chunk = non_empty_sentences[i:i + pov_chunk_size]
            chunk_counts = {"1st": 0, "2nd": 0, "3rd": 0}

            for sentence in chunk:
                for token in sentence:
                    match token["1st_2nd_3rd"]:
                        case ["1"]: chunk_counts["1st"] += 1
                        case ["2"]: chunk_counts["2nd"] += 1
                        case ["3"]: chunk_counts["3rd"] += 1
                        case _: pass

            total = sum(chunk_counts.values())
            if total:
                pov_over_time["1st"].append((chunk_counts["1st"] / total) * 100)
                pov_over_time["2nd"].append((chunk_counts["2nd"] / total) * 100)
                pov_over_time["3rd"].append((chunk_counts["3rd"] / total) * 100)
            else:
                pov_over_time["1st"].append(0)
                pov_over_time["2nd"].append(0)
                pov_over_time["3rd"].append(0)


        axs = self.figure.subplots(5, 2)

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

        ax = axs[4, 0]

        values = [pov_counts.get("1st", 0), pov_counts.get("2nd", 0), pov_counts.get("3rd", 0)]
        labels = ["1st", "2nd", "3rd"]

        if sum(values) > 0:
            ax.pie(values, labels=labels, autopct="%1.1f%%")
        else:
            ax.text(0.5, 0.5, "No POV data", ha="center", va="center")
            ax.axis("off")

        ax.set_title("POV Percentages")

        ax = axs[4, 1]
        chunk_x = np.arange(1, len(pov_over_time["1st"]) + 1)

        if len(chunk_x):
            ax.plot(chunk_x, pov_over_time["1st"], label="1st")
            ax.plot(chunk_x, pov_over_time["2nd"], label="2nd")
            ax.plot(chunk_x, pov_over_time["3rd"], label="3rd")
            ax.set_xlabel(f"Chunk Index ({pov_chunk_size} sentences/chunk)")
            ax.set_ylabel("POV Share (%)")
            ax.legend()
        else:
            ax.text(0.5, 0.5, "No POV trend data", ha="center", va="center", transform=ax.transAxes)

        ax.set_title("POV Over Time")

        self.canvas.draw()

        #gets passive sentences
        sentences_index= [index for index, boolean in enumerate(passive_flags) if boolean]
        self.passive_sentences = [
            " ".join(token["text"] for token in non_empty_sentences[i])
            for i in sentences_index
        ]
        if self.passive_sentences:
            self.open_passive_popup()

        # get sentences with first or second person
        self.first_second_person_sentences = [
            " ".join(word["text"] for word in sentence)
            for sentence in non_empty_sentences
            if any(word["1st_2nd_3rd"] == ["1"] or word["1st_2nd_3rd"] == ["2"] for word in sentence)
        ]
        if self.first_second_person_sentences:
            self.open_pronoun_popup()

    def open_passive_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Passive Sentences")
        dialog.resize(520, 360)

        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        title_on_page = QLabel("Sentences Dected as Being Passive:")
        title_on_page.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_on_page)

        for sentence in self.passive_sentences:
            text = QLabel(sentence)
            text.setAlignment(Qt.AlignCenter)
            text.setWordWrap(True)  
            content_layout.addWidget(text)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        export_btn = QPushButton("Export Sentences")
        export_btn.clicked.connect(self.export_passive_sentences)
        layout.addWidget(export_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.exec()

    def open_pronoun_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("First or Second Person")
        dialog.resize(520, 360)

        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        title_on_page = QLabel("Sentences Dected For having First or Second Person:")
        title_on_page.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_on_page)

        for sentence in self.first_second_person_sentences:
            text = QLabel(sentence)
            text.setAlignment(Qt.AlignCenter)
            text.setWordWrap(True)  
            content_layout.addWidget(text)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        export_btn = QPushButton("Export Sentences")
        export_btn.clicked.connect(self.export_passive_sentences)
        layout.addWidget(export_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.exec()

    def export_passive_sentences(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Text Files (*.txt)"
        )

        if file_path:
            if not file_path.endswith(".txt"):
                file_path += ".txt"

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(" ".join(self.passive_sentences))
