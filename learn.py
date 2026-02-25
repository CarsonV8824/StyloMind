import spacy



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


if __name__ == "__main__":
    text = """My name is Carson. Learning python at STA, I have gained massive knowledge."""
    print(make_text_into_sentences_with_part_of_speech(text))