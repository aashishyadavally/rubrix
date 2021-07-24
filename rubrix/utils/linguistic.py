"""Utilities to extract linguistic features for a word/phrase/sentence
using trained language pipelines from SpaCy.
"""
import spacy

from rubrix.utils.lang import retrieve_spacy_model, SPACY_MODEL_SMALL


def extract_entities(text):
    """Extracts named-entity pairs from given text based on named-entity
    recognition labels.

    Arguments:
    ----------
        text (str):
            Word/Phrase/Sentence

    Returns:
    --------
        entities (list):
            List of tuples mapping named entities to corresponding labels.
    """
    model = retrieve_spacy_model(SPACY_MODEL_SMALL)
    text = model(text)
    entities = [(entity.text, entity.label_) for entity in text.ents]
    return entities


def extract_nouns(text):
    """Extracts nouns from given text based on parts-of-speech tags.

    Arguments:
    ----------
        text (str):
            Word/Phrase/Sentence

    Returns:
    --------
        pos_tags (list):
            List of tuples mapping tokens in the sentence to corresponding
            parts-of-speech tags.
    """
    model = retrieve_spacy_model(SPACY_MODEL_SMALL)
    text = model(text)
    pos_tags = [(word.tag_, word.pos_) for word in text]
    return pos_tags


def extract_features(text):
    """Extracts linguistic features based on a custom logic to enable
    object-based query filtering.

    One advantage of NOUN-based filtering is that unknown words, by default
    are tagged as nouns in Spacy.

    Notes:
    ------
    1. Custom logic can be implemented here to extract features
    according to the list of objects in the dataset.

    2. There's a 3X speed markup in using small v/s medium versions of trained
    English language pipelines. Furthermore, accuracy of POS Tagging models
    for both are 0.97, and the F-scores for named-entity recognition are 0.84
    and 0.85 respectively. Recommend using the medium pipeline for word2vec
    feature retrieval, and small pipeline for other linguistic features.

    Arguments:
    ----------
        text (str):
            Word/Phrase/Sentence

    Returns:
    --------
        features (list):
            List of extracted features.
    """
    model = retrieve_spacy_model(SPACY_MODEL_SMALL)
    text = model(text)

    features = []

    entity_labels = [entity.label_.lower() for entity in text.ents]

    if "person" in entity_labels:
        features.append("person")

    for word in text:
        if word.pos_.lower() == "noun":
            features.append(str(word))

    return features


# TODO: Test function - remove before moving to production.
if __name__ == '__main__':
    import time
    start = time.time()
    print(extract_features('John kicked the ball.'))
    end = time.time()
    print(f'Time to extract features: {end - start}')
