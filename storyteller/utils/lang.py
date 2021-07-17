"""Utility to retrieve various trained language pipelines from SpaCy.
These models are useful to extract linguistic features such as
tokens, parts-of-speech tags, named-entities, dependency tags,
word2vec embeddings, etc.
"""
import subprocess

import spacy


# Check the following link to compare English language Spacy trained
# pipelines:  https://spacy.io/models/en

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
    """Retrieves trained language pipeline from within SpaCy.
    If not available, it is downloaded.

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
