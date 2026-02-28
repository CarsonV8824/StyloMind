import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from typing import Any

NLP = None


def _get_nlp():
    global NLP
    if NLP is None:
        try:
            # NER is not used by the current feature set, so disable it for faster load.
            NLP = spacy.load("en_core_web_sm", disable=["ner"])
        except OSError as exc:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' is not installed. "
                "Run: python -m spacy download en_core_web_sm"
            ) from exc
    return NLP

def read_text_file(path: str) -> str:
    """Read text robustly across common encodings on Windows."""
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def make_text_into_sentences_with_part_of_speech(text: str) -> list[list[dict[str, Any]]]:
    """Return sentence-token data with POS/dependency plus style-relevant token features."""
    doc = _get_nlp()(text)
    list_of_sentences = []

    for sent in doc.sents:
        sentence = []
        for token in sent:
            sentence.append(
                {
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "tag": token.tag_,
                    "dep": token.dep_,
                    "is_stop": token.is_stop,
                    "is_punct": token.is_punct,
                    "is_upper": token.is_upper,
                    "is_title": token.is_title,
                    "morph": str(token.morph),
                    "length": len(token.text),
                    "1st_2nd_3rd":token.morph.get("Person")
                }
            )
        list_of_sentences.append(sentence)

    return list_of_sentences

def _cosine_tfidf(doc1: str, doc2: str, *, analyzer: str = "word", ngram_range: tuple[int, int] = (1, 1)) -> float:
    vectorizer = TfidfVectorizer(analyzer=analyzer, lowercase=True, ngram_range=ngram_range, sublinear_tf=True)
    matrix = vectorizer.fit_transform([doc1, doc2])
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def _sentence_length_bucket(length: int) -> str:
    if length <= 8:
        return "short"
    if length <= 18:
        return "medium"
    return "long"


def structure_document(text: str) -> str:
    sents = make_text_into_sentences_with_part_of_speech(text)
    feats: list[str] = []

    for sent in sents:
        non_punct = [t for t in sent if not t["is_punct"]]
        if not non_punct:
            continue

        pos_seq = [t["pos"] for t in non_punct]
        feats.extend(f"PD:{t['pos']}:{t['dep']}" for t in non_punct)

        for i in range(len(pos_seq) - 1):
            feats.append(f"P2:{pos_seq[i]}>{pos_seq[i + 1]}")
        for i in range(len(pos_seq) - 2):
            feats.append(f"P3:{pos_seq[i]}>{pos_seq[i + 1]}>{pos_seq[i + 2]}")

        feats.append(f"SLEN:{_sentence_length_bucket(len(non_punct))}")

    return " ".join(feats)

def structure_similarity(text1: str, text2: str) -> float:
    doc1 = structure_document(text1)
    doc2 = structure_document(text2)
    return _cosine_tfidf(doc1, doc2, analyzer="word", ngram_range=(1, 2))


def style_document(text: str) -> str:
    sents = make_text_into_sentences_with_part_of_speech(text)
    feats: list[str] = []

    for sent in sents:
        non_punct = [t for t in sent if not t["is_punct"]]
        if not non_punct:
            continue

        for t in non_punct:
            feats.append(f"POS:{t['pos']}")
            feats.append(f"TAG:{t['tag']}")
            feats.append(f"DEP:{t['dep']}")
            feats.append(f"UPPER:{int(t['is_upper'])}")
            feats.append(f"TITLE:{int(t['is_title'])}")

            if t["is_stop"]:
                feats.append(f"FUNC:{t['lemma'].lower()}")
            elif t["pos"] in {"ADJ", "ADV", "VERB", "NOUN", "PROPN"}:
                feats.append(f"LEX:{t['lemma'].lower()}")

            if t["length"] <= 3:
                feats.append("LEN:short")
            elif t["length"] <= 7:
                feats.append("LEN:medium")
            else:
                feats.append("LEN:long")

    punct_counts = {
        "PERIOD": text.count("."),
        "COMMA": text.count(","),
        "SEMICOLON": text.count(";"),
        "COLON": text.count(":"),
        "QUESTION": text.count("?"),
        "EXCLAMATION": text.count("!"),
        "QUOTE": text.count('"') + text.count("'"),
        "DASH": text.count("-"),
    }
    for key, count in punct_counts.items():
        if count:
            feats.extend([f"PUNCT:{key}"] * count)

    return " ".join(feats)

def style_similarity(text1: str, text2: str) -> float:
    style_doc1 = style_document(text1)
    style_doc2 = style_document(text2)

    marker_score = _cosine_tfidf(style_doc1, style_doc2, analyzer="word", ngram_range=(1, 2))
    char_score = _cosine_tfidf(text1, text2, analyzer="char_wb", ngram_range=(3, 5))

    # Character n-grams are often more robust for author-style cues than raw word overlap.
    return (0.6 * char_score) + (0.4 * marker_score)

if __name__ == "__main__":
    #a = read_text_file("services/data/chat_gpt.txt")
    #b = read_text_file("services/data/copiolit.txt")
    print([
        word["pos"]
        for sentence in make_text_into_sentences_with_part_of_speech("You are the best")
        for word in sentence
    ])
    """
    structure_score = structure_similarity(a, b)
    style_score = style_similarity(a, b)
    print("Structure similarity:", structure_score, "=>", round(structure_score * 100, 2), "%")
    print("Style similarity:", style_score, "=>", round(style_score * 100, 2), "%")"""

"""from pathlib import Path
import numpy as np

def percentile(value, arr):
    arr = np.array(arr, dtype=float)
    return float((arr <= value).mean() * 100.0)

ref_paths = list(Path("samples").glob("*.txt"))
refs = [read_text_file(str(p)) for p in ref_paths]

s_ab = style_similarity(a, b)
s_base = [style_similarity(a, r) for r in refs]

p = percentile(s_ab, s_base)
z = (s_ab - float(np.mean(s_base))) / (float(np.std(s_base)) + 1e-9)

print(f"Style raw: {s_ab:.4f}")
print(f"Style percentile: {p:.1f}")
print(f"Style z-score: {z:.2f}")
"""
