import spacy

def make_text_into_sentences_with_part_of_speech(text:str) -> list[list[tuple[str, str]]]:
    """returns your text with each sentence in it's own list and each word with its part of speech"""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    list_of_sentences = []
    sentence = []
    for token in doc:
        if token.text == "." or token.text == "?" or token.text == "!":
            sentence.append((token.text, token.pos_))
            list_of_sentences.append(sentence)
            sentence = []
            continue
        sentence.append((token.text, token.pos_))

    with open("text.txt", "w") as f:
        f.write(str(list_of_sentences))

    return list_of_sentences

if __name__ == "__main__":
    text = ("""My Name is Carson and I like python. Do you?""")
    print(make_text_into_sentences_with_part_of_speech(text))