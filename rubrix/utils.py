"""Contains important utilities which assist query procesing pipeline.
"""
import sys
import json
import heapq
import subprocess
from pathlib import Path

import numpy as np

import scipy
from scipy.spatial.distance import cosine, euclidean

import spacy

import dotproduct
from rubrix import pathfinder


# Small-size (12MB) trained English language Spacy pipeline
# No trained word2vec embeddings
SPACY_MODEL_SMALL = 'en_core_web_sm'

# Medium-size (43MB) trained English language Spacy pipeline
# word2vec embeddings for 685K keys with 20K unique vectors (300 dimensions).
SPACY_MODEL_MEDIUM = 'en_core_web_md'

# Large (741) trained English language Spacy pipeline
# word2vec embeddings for 685K keys with 685K unique vectors (300 dimensions).
SPACY_MODEL_LARGE = 'en_core_web_lg'


def retrieve_spacy_model(lang):
    """Utility to retrieve various trained language pipelines from SpaCy.

    These models are useful to extract linguistic features such as
    tokens, parts-of-speech tags, named-entities, dependency tags,
    word2vec embeddings, etc.

    If not available the trained language pipeline is downloaded.

    Check the following link to compare English language Spacy trained
    pipelines:  https://spacy.io/models/en

    Arguments:
    ----------
        lang (str):
            Key to trained SpaCy language pipeline.

    Returns:
    --------
        model (spacy.lang)
            Trained SpaCy language pipeline.
    """
    if not spacy.util.is_package(lang):
        subprocess.call(f'python -m spacy download {lang}', shell=True)

    model = spacy.load(lang)
    return model



def extract_entities(text, model=SPACY_MODEL_SMALL):
    """Utility to extract named-entity pairs from given text, according to
    the trained language pipeline from SpaCy.

    Arguments:
    ----------
        text (str):
            Word/Phrase/Sentence
        model (spacy.lang)
            Trained SpaCy language pipeline.
            By default, 'en-core-web-sm' is recommended for this utility.

    Returns:
    --------
        entities (list):
            List of tuples mapping named entities to corresponding labels.
    """
    model = retrieve_spacy_model(model)
    text = model(text)
    entities = [(entity.text, entity.label_) for entity in text.ents]
    return entities


def extract_nouns(text, model=SPACY_MODEL_SMALL):
    """Utility to extract nouns from given text based on parts-of-speech
    tags extracted by trained language pipeline from SpaCy.

    Arguments:
    ----------
        text (str):
            Word/Phrase/Sentence
        model (spacy.lang)
            Trained SpaCy language pipeline.
            By default, 'en-core-web-sm' is recommended for this utility.

    Returns:
    --------
        pos_tags (list):
            List of tuples mapping tokens in the sentence to corresponding
            parts-of-speech tags.
    """
    model = retrieve_spacy_model(model)
    text = model(text)
    pos_tags = [(word.tag_, word.pos_) for word in text]
    return pos_tags


def extract_features(text, model):
    """Utility to extract linguistic features based on a custom logic so as
    to enable object-based query filtering.

    One advantage of NOUN-based filtering is that unknown words, by default
    are tagged as nouns in Spacy.

    Notes:
    ------
    1. Custom logic can be implemented here to extract features according to
    the list of objects in the dataset.

    2. There's a 3X speed markup in using small v/s medium versions of trained
    English language pipelines. Furthermore, accuracy of POS Tagging models
    for both are 0.97, and the F-scores for named-entity recognition are 0.84
    and 0.85 respectively. Recommend using the medium pipeline for word2vec
    feature retrieval, and small pipeline for other linguistic features.

    Arguments:
    ----------
        text (str):
            Word/Phrase/Sentence
        model (spacy.lang)
            Trained SpaCy language pipeline.
            By default, 'en-core-web-sm' is recommended for this utility.

    Returns:
    --------
        features (list):
            List of extracted features.
    """
    model = retrieve_spacy_model(model)
    text = model(text)

    features = []

    entity_labels = [entity.label_.lower() for entity in text.ents]

    if "person" in entity_labels:
        features.append("person")

    for word in text:
        if word.pos_.lower() == "noun":
            features.append(str(word))

    return features


def dot_product(array, other_array):
    """Utility to compute dot product of two arrays as a distance metric.
    It is a variation of cosine distance and is useful in cases where the
    length varies, and captures semantic information.

    Arguments:
    ----------
        array (array_like object):
            Input array.
        other_array (array_like object):
            Input array.

    Returns:
    --------
        (float):
            Dot product.
    """
    return np.inner(array, other_array)


def cdot_product(array, other_array):
    """Utility to compute dot product between two arrays - it is significantly
    faster than corresponding dot product computation by Numpy and makes use
    of parallel processing library OpenMp.

    Check rubrix/source/dotproduct.c for more details.
    """
    data = [array.tolist(), other_array.tolist()]
    return dotproduct.dot_product_optimized(*data)


def cosine_distance(array, other_array):
    """Utility to compute the cosine distance between two 1-D arrays.

    Arguments:
    ----------
        array (array_like object):
            Input array.
        other_array (array_like object):
            Input array.

    Returns:
    --------
        (float):
            Cosine distance.
    """
    return cosine(array, other_array)


def euclidean_distance(array, other_array):
    """Utility to compute the Euclidean distance between two 1-D arrays.

    Arguments:
    ----------
        array (array_like object):
            Input array.
        other_array (array_like object):
            Input array.

    Returns:
    --------
        (float):
            Euclidean distance.
    """
    return euclidean(array, other_array)


def get_similar_words(word, names_file, n=3):
    """Utility to retrieve `n` similar words based on word2vec feature
    similarity.

    Arguments:
    ----------
        word (str):
            Base word.
        names_file (pathlib.Path):
            Path to file containing list of objects YOLO is trained on.
        n (int):
            Number of similar words to extract.

    Returns:
    --------
        most_similar_words (list):
            List of top-N similar words.
    """
    names_path = pathfinder.get('rubrix', 'search', 'darknet',
                                'data', names_file)

    try:
        names = [name.rstrip() for name in open(names_path).readlines()]
    except:
        print('PathError: Path to names file is incorrect.')
        sys.exit()

    model = retrieve_spacy_model(SPACY_MODEL_MEDIUM)
    # Disabling pipeline components computing linguistic features saves
    # time, as these components are not necessary for word2vec similarity
    # score computation.
    model.disable_pipes(['tok2vec', 'tagger', 'parser', 'attribute_ruler',
                         'lemmatizer', 'ner'])

    word = model(word)
    word_similarities = [word.similarity(model(name)) for name in names]

    most_similar_tuples = heapq.nlargest(n,
                                         enumerate(word_similarities),
                                         key=lambda x: x[1])
    most_similar_words_idx = [elem[0] for elem in most_similar_tuples]
    most_similar_words = [names[idx] for idx in most_similar_words_idx]
    return most_similar_words


def fix_paths_in_index(index_path, emb_path):
    """Utility to fix paths in inverse image index file (``index.json``)
    and inverse embedding index file (``imageEmbeddingLocations.json``).

    Running the bash script ``setup.sh`` in ``rubrix/search`` directory
    sets up the inverse image index and image embedding index JSON files.
    However, this script takes close to an hour for completion.

    Given both the index files, this is an alternative to simply fix the
    paths in, thus enabling faster code reproducibility.

    Arguments:
    ----------
        index_path (pathlib.Path):
            Absolute path to inverse image index file.
        emb_path (pathlib.Path):
            Absolute path to image embeddings index file.
    """
    for path_to_index in [index_path, emb_path]:
        root = pathfinder.get_root()

        with open(path_to_index, 'r') as index_file:
            index = json.load(index_file)

        for key, values in index.items():
            new_values = []
            for path in values:
                suffix = str(path)[str(path).find('rubrix'):]
                suffix = '/'.join(suffix.split('/')[1:])
                new_values.append(str(root / Path(suffix)))
            index[key] = new_values

        with open(path_to_index, 'w') as index_file:
            json.dump(index, index_file, indent=4)
