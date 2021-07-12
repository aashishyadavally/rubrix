import heapq
import subprocess
from pathlib import Path

import spacy


def retrieve_spacy_language(lang):
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


def get_similar_words(word, names_file, n=3):
	"""

	Arguments:
	----------

	Returns:
	--------
	"""
	names_path = Path('darknet') / 'data' / names_file

	try:
		names = [name.rstrip() for name in open(names_path).readlines()]
	except:
		print('PathError: Path to names file is incorrect.')

	model = retrieve_spacy_language('en_core_web_md')

	word = model(word)
	word_similarities = [word.similarity(model(name)) for name in names]

	most_similar_tuples = heapq.nlargest(n, enumerate(word_similarities), 
										   key=lambda x: x[1])
	most_similar_words_idx = [elem[0] for elem in most_similar_tuples]

	most_similar_words = [names[idx] for idx in most_similar_words_idx]

	return most_similar_words


if __name__ == '__main__':
	tags = get_similar_words('music', 'coco.names')
	print(tags)
