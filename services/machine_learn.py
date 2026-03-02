import pandas as pd
from learn import style_document

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re

import joblib

def make_model() -> None:
    df = pd.read_csv("services/ML Stuff/ai_vs_human_dataset.csv")

    texts = df["text"].to_list()
    labels = df["label"].to_list()

    # Convert labels to numeric
    human_or_ai_data = []
    for label in labels:
        match label:
            case "ai":
                human_or_ai_data.append(1)
            case "human":
                human_or_ai_data.append(0)
            case _:
                raise ValueError("Invalid label. Only 'ai' and 'human' allowed.")

    # Build processed text features
    words_data = []
    for index, text in enumerate(texts):
        styled = style_document(text) or ""
        combined = (styled).strip()

        print(f"[{index}] -> '{combined}'")

        if not combined:
            combined = "emptydoc"

        words_data.append(combined)

    # Vectorize
    tfidf = TfidfVectorizer(stop_words=None)
    X = tfidf.fit_transform(words_data)

    # Train model
    model = LogisticRegression()
    model.fit(X, human_or_ai_data)

    # Save model + vectorizer
    joblib.dump(model, "services/ML Stuff/ridge_model.pkl")
    joblib.dump(tfidf, "services/ML Stuff/tfidf_vectorizer.pkl")

def test_text(text: str) -> dict:
    if not text:
        raise ValueError("Input text is required")

    # Load model + vectorizer
    model: LogisticRegression = joblib.load("services/ML Stuff/ridge_model.pkl")
    tfidf: TfidfVectorizer = joblib.load("services/ML Stuff/tfidf_vectorizer.pkl")

    final = {}
    sentences = re.split(r'(?<=[.!?])\s+', text)
    print(sentences)

    for index, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        styled = style_document(sentence) or ""
        combined = (styled).strip()

        x = tfidf.transform([combined])  # <-- transform, not fit_transform
        result = model.predict(x)[0]     # <-- extract scalar

        final[f"percentage of ai in sentence {index+1}"] = f"{float(result) * 100:.2f}%"

    return final

if __name__ == "__main__":
    print(test_text("The silver fox wandered through the forgotten library, pausing to read the dust-covered spines of books that no one had touched in a century. Nye uses a metaphor to show how people should have emphathy towards others."))