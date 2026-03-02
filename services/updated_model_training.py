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
#sentences = re.split(r'(?<=[.!?])\s+', text)
def make_model() -> None:
    df = pd.read_csv("services/ML Stuff/ai_vs_human_dataset.csv")

    texts = df["text"].to_list()
    labels = df["label"].to_list()

    labels = [1 if label == "ai" else 0 for label in labels]
    
    combined = zip(texts, labels)

    x_data = []
    y_data = []
    for text, label in list(combined):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        print(sentences)
        for sentence in sentences:
            x_data.append(style_document(sentence))
            y_data.append(label)
    print(x_data, y_data)
    

    # Vectorize
    tfidf = TfidfVectorizer(stop_words=None)
    X = tfidf.fit_transform(x_data)

    # Train model
    Y = y_data

    model = LogisticRegression()
    model.fit(X, Y)

    # Save model + vectorizer
    joblib.dump(model, "services/ML Stuff/ridge_model.pkl")
    joblib.dump(tfidf, "services/ML Stuff/tfidf_vectorizer.pkl")

if __name__ == "__main__":
    make_model()