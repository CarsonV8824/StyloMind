import spacy
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
import numpy as np

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

def convert_data_from_str_to_data(sentence_struct: list[list[tuple[str, str, str]]]) -> tuple:
    """Converts the data into a matrix of numbers so ML can understand data"""
    # rows like [POS, DEP] per token
    pos_dep_pairs = [[pos, dep] for sentence in sentence_struct for _, pos, dep in sentence]
    categorical_feature = np.array(pos_dep_pairs, dtype=object)

    try:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    except TypeError:
        encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")

    encoded_feature = encoder.fit_transform(categorical_feature)

    print("Categories:", encoder.categories_)  # [POS categories, DEP categories]
    print("Feature names:", encoder.get_feature_names_out(["pos", "dep"]))
    print("OneHotEncoded feature:\n", encoded_feature)
    return encoded_feature, encoder

def train_model(data):
    """trains the model"""
    X, encoder = convert_data_from_str_to_data()
    log_reg = LinearRegression(max_iter=200)
    log_reg.fit(X)

if __name__ == "__main__":
    text = """My name is Carson. Learning python at STA, I have gained massive knowledge."""
    data = make_text_into_sentences_with_part_of_speech(text)
    convert_data_from_str_to_data(data)
    