import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import services.graph_NLP as textTraining

# ----------------------------
# Helper Functions
# ----------------------------

def _detokenize(tokens: list[dict]) -> str:
    contraction_suffixes = {"n't", "'s", "'m", "'re", "'ve", "'ll", "'d"}
    no_space_before = {".", ",", "!", "?", ";", ":", "%", ")", "]", "}"}
    no_space_after = {"(", "[", "{"}
    double_quote_tokens = {'"', "“", "”"}

    text = ""
    in_double_quote = False

    for token in tokens:
        piece: str = token["text"].strip()
        if not piece:
            continue

        if not text:
            text = piece
        elif piece in double_quote_tokens:
            if in_double_quote:
                text += '"'
                in_double_quote = False
            else:
                if text[-1] not in no_space_after:
                    text += " "
                text += '"'
                in_double_quote = True
        elif piece.startswith("'") or piece in contraction_suffixes:
            text += piece
        elif piece in no_space_before or re.fullmatch(r"[.,!?;:%)\]}]+", piece):
            text += piece
        elif text[-1] in no_space_after:
            text += piece
        else:
            text += f" {piece}"

    text = re.sub(r"\b([A-Za-z]+)\s+n\s*'\s*t\b", r"\1n't", text)
    text = re.sub(r"\b([A-Za-z]+)\s*'\s*(nt|s|m|re|ve|ll|d)\b", r"\1'\2", text)

    return text


# ----------------------------
# Analyzer Class
# ----------------------------

class TextDashboardAnalyzer:

    def __init__(self, figure=None, canvas=None):
        self.figure = figure
        self.canvas = canvas

        self.passive_sentences = []
        self.first_second_person_sentences = []
        self.contraction_sentences = []

    # ----------------------------
    # Main Entry Point
    # ----------------------------

    def analyze_text(self, chosen_text: str):

        sentence_data = textTraining.make_text_into_sentences_with_part_of_speech(chosen_text)

        non_empty_sentences = [s for s in sentence_data if s]
        if not non_empty_sentences:
            self._render_empty_dashboard()
            return

        metrics = self._analyze_sentences(non_empty_sentences)

        lemmas = [
            t["lemma"].lower()
            for t in metrics["flat_non_punct"]
            if t["lemma"]
        ]

        lexical_diversity = self._compute_lexical_diversity(lemmas)
        pov_over_time = self._compute_pov_over_time(non_empty_sentences)

        self._render_dashboard(metrics, lexical_diversity, pov_over_time)

        (
            self.passive_sentences,
            self.contraction_sentences,
            self.first_second_person_sentences,
        ) = self._extract_special_sentences(non_empty_sentences, metrics)

    # ----------------------------
    # Sentence Analysis
    # ----------------------------

    def _analyze_sentences(self, sentences):

        sentence_lengths = []
        passive_flags = []
        contraction_flags = []
        flat_non_punct = []

        contraction_suffixes = {"n't", "'s", "'m", "'re", "'ve", "'ll", "'d"}

        for sentence in sentences:
            non_punct = [t for t in sentence if not t["is_punct"]]
            sentence_lengths.append(len(non_punct))

            passive_flags.append(any(t["dep"] in {"auxpass", "nsubjpass"} for t in sentence))
            contraction_flags.append(any(t["text"] in contraction_suffixes for t in sentence))

            flat_non_punct.extend(non_punct)

        return {
            "sentence_lengths": sentence_lengths,
            "passive_flags": passive_flags,
            "contraction_flags": contraction_flags,
            "flat_non_punct": flat_non_punct,
        }

    # ----------------------------
    # Trend Functions
    # ----------------------------

    def _compute_lexical_diversity(self, lemmas, chunk_size=120):
        scores = []
        for i in range(0, len(lemmas), chunk_size):
            chunk = lemmas[i:i + chunk_size]
            if chunk:
                scores.append(len(set(chunk)) / len(chunk))
        return scores

    def _compute_pov_over_time(self, sentences, chunk_size=20):
        pov_over_time = {"1st": [], "2nd": [], "3rd": []}

        for i in range(0, len(sentences), chunk_size):
            chunk = sentences[i:i + chunk_size]
            counts = {"1st": 0, "2nd": 0, "3rd": 0}

            for sentence in chunk:
                for token in sentence:
                    match token["1st_2nd_3rd"]:
                        case ["1"]: counts["1st"] += 1
                        case ["2"]: counts["2nd"] += 1
                        case ["3"]: counts["3rd"] += 1
                        case _: pass

            total = sum(counts.values())
            for key in counts:
                pov_over_time[key].append((counts[key] / total) * 100 if total else 0)

        return pov_over_time

    # ----------------------------
    # Rendering
    # ----------------------------

    def _render_dashboard(self, metrics, lexical_diversity, pov_over_time):

        self.figure.clear()
        axs = self.figure.subplots(2, 2)

        ax = axs[0, 0]
        sns.histplot(metrics["sentence_lengths"], bins=12, kde=True, ax=ax)
        ax.set_title("Sentence Length Distribution")

        ax = axs[0, 1]
        if lexical_diversity:
            ax.plot(lexical_diversity)
        ax.set_title("Lexical Diversity")

        ax = axs[1, 0]
        chunk_x = np.arange(1, len(pov_over_time["1st"]) + 1)
        if len(chunk_x):
            ax.plot(chunk_x, pov_over_time["1st"], label="1st")
            ax.plot(chunk_x, pov_over_time["2nd"], label="2nd")
            ax.plot(chunk_x, pov_over_time["3rd"], label="3rd")
            ax.legend()
        ax.set_title("POV Over Time")

        self.figure.tight_layout()
        self.canvas.draw()

    def _render_empty_dashboard(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, "No sentence data available",
                ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
        self.canvas.draw()

    # ----------------------------
    # Special Sentence Extraction
    # ----------------------------

    def _extract_special_sentences(self, sentences, metrics):
        """sentences = normalized sentence data and metrics = self._analyze_sentences(non_empty_sentences)"""
        passive_sentences = [
            _detokenize(sentences[i])
            for i, flag in enumerate(metrics["passive_flags"])
            if flag
        ]

        contraction_sentences = [
            _detokenize(sentences[i])
            for i, flag in enumerate(metrics["contraction_flags"])
            if flag
        ]

        first_second_sentences = [
            _detokenize(sentence)
            for sentence in sentences
            if any(t["1st_2nd_3rd"] in (["1"], ["2"]) for t in sentence)
        ]

        return passive_sentences, contraction_sentences, first_second_sentences