"""Utilities to extract similar words/sentences, semantic similarity
scores from various metrics, etc.
"""
import sys
import heapq

import numpy as np

from scipy.spatial.distance import cosine, euclidean

from rubrix import pathfinder
from rubrix.utils.lang import retrieve_spacy_model, SPACY_MODEL_MEDIUM


def dot_product(array, other_array):
    """Computes dot product of two arrays as a distance metric.
    It is a variation of cosine distance and is useful in cases
    where the length varies, and captures semantic information.

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


def cosine_distance(array, other_array):
    """Computes the cosine distance between two 1-D arrays.

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
    """Computes the Euclidean distance between two 1-D arrays.

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
    """Retrieve `n` similar words based on word2vec feature similarity.

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


# TODO: Test function - remove before moving to production.
if __name__ == '__main__':
    import time
    start = time.time()
    words = get_similar_words('music', 'coco.names')
    print(words)
    end = time.time()
    print(f'Time to get similar words: {end - start}')
