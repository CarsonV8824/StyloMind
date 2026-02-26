import spacy
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from typing import Any

def make_text_into_sentences_with_part_of_speech(text: str) -> list[list[tuple[str, str, str]]]:
    """Returns text with each sentence in its own list and each word with its part of speech."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    list_of_sentences = []

    for sent in doc.sents:
        sentence = []
        for token in sent:
            sentence.append((token.text, token.pos_, token.dep_))
        list_of_sentences.append(sentence)

    return list_of_sentences

def structure_vector(text: str):
    sents = make_text_into_sentences_with_part_of_speech(text)
    tags = [f"{pos}:{dep}" for sent in sents for _, pos, dep in sent]
    return Counter(tags)

def structure_similarity(text1: str, text2: str) -> float:
    c1 = structure_vector(text1)
    c2 = structure_vector(text2)

    keys = sorted(set(c1) | set(c2))
    v1 = np.array([c1[k] for k in keys], dtype=float).reshape(1, -1)
    v2 = np.array([c2[k] for k in keys], dtype=float).reshape(1, -1)

    return float(cosine_similarity(v1, v2)[0][0]) 

if __name__ == "__main__":
    a = "My name is Carson. I am learning Python. Studing Python, Carson also enjoys Music"
    b = "Her name is Maya. She is studying Java."
    score = structure_similarity(a, b)
    print("Structure similarity:", score, "=>", round(score * 100, 2), "%")


    