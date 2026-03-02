import pandas as pd
try:
    from learn import style_document
except ModuleNotFoundError:
    from services.learn import style_document

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

def test_text_for_ai(text: str) -> dict:
    if not text:
        raise ValueError("Input text is required")

    # Load model + vectorizer
    model: LogisticRegression = joblib.load("services/ML Stuff/ridge_model.pkl")
    tfidf: TfidfVectorizer = joblib.load("services/ML Stuff/tfidf_vectorizer.pkl")

    final = {}
    sentences = re.split(r'(?<=[.!?])\s+', text)
    #print(sentences)

    for index, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        styled = style_document(sentence) or ""
        combined = (styled).strip()

        x = tfidf.transform([combined])  # <-- transform, not fit_transform
        result = model.predict(x)[0]     # <-- extract scalar

        final[sentences[index]] = float(result)

    return final

if __name__ == "__main__":
    print(test_text_for_ai("A quiet breeze drifted through the open window, carrying the scent of spring into the room."))
