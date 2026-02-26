import spacy
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from typing import Any

NLP = spacy.load("en_core_web_sm")

def make_text_into_sentences_with_part_of_speech(text: str) -> list[list[dict[str, Any]]]:
    """Return sentence-token data with POS/dependency plus style-relevant token features."""
    doc = NLP(text)
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
                }
            )
        list_of_sentences.append(sentence)

    return list_of_sentences

def structure_vector(text: str):
    sents = make_text_into_sentences_with_part_of_speech(text)
    tags = [f"{token['pos']}:{token['dep']}" for sent in sents for token in sent]
    return Counter(tags)

def structure_similarity(text1: str, text2: str) -> float:
    c1 = structure_vector(text1)
    c2 = structure_vector(text2)

    keys = sorted(set(c1) | set(c2))
    v1 = np.array([c1[k] for k in keys], dtype=float).reshape(1, -1)
    v2 = np.array([c2[k] for k in keys], dtype=float).reshape(1, -1)

    return float(cosine_similarity(v1, v2)[0][0]) 

def style_vector(text: str) -> Counter:
    sents = make_text_into_sentences_with_part_of_speech(text)
    feats: Counter = Counter()
    sentence_lengths = []

    for sent in sents:
        non_punct = [t for t in sent if not t["is_punct"]]
        sentence_lengths.append(len(non_punct))
        for t in non_punct:
            feats[f"POS:{t['pos']}"] += 1
            feats[f"TAG:{t['tag']}"] += 1
            feats[f"DEP:{t['dep']}"] += 1
            feats[f"LEMMA:{t['lemma'].lower()}"] += 1
            feats[f"STOP:{int(t['is_stop'])}"] += 1
            feats[f"UPPER:{int(t['is_upper'])}"] += 1
            feats[f"TITLE:{int(t['is_title'])}"] += 1
            feats[f"MORPH:{t['morph']}"] += 1
            if t["length"] <= 3:
                feats["LEN:short"] += 1
            elif t["length"] <= 7:
                feats["LEN:medium"] += 1
            else:
                feats["LEN:long"] += 1

    if sentence_lengths:
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        feats[f"SENT_AVG:{round(avg_len)}"] += 1
        feats[f"SENT_COUNT:{len(sentence_lengths)}"] += 1

    return feats

def style_similarity(text1: str, text2: str) -> float:
    c1 = style_vector(text1)
    c2 = style_vector(text2)

    keys = sorted(set(c1) | set(c2))
    v1 = np.array([c1[k] for k in keys], dtype=float).reshape(1, -1)
    v2 = np.array([c2[k] for k in keys], dtype=float).reshape(1, -1)

    return float(cosine_similarity(v1, v2)[0][0])

if __name__ == "__main__":
    with open("chat_gpt.txt", "r") as f:
        a = f.read()
    with open("copiolit.txt", "r") as f:
        b = f.read()
    structure_score = structure_similarity(a, b)
    style_score = style_similarity(a, b)
    print("Structure similarity:", structure_score, "=>", round(structure_score * 100, 2), "%")
    print("Style similarity:", style_score, "=>", round(style_score * 100, 2), "%")


    
