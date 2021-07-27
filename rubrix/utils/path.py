"""Utility to fix paths in ``index.json`` and ``imageEmbeddingLocations.json``.

Running the bash script ``setup.sh`` in ``rubrix/search`` directory sets up
the inverse image index and image embedding index JSON files. However, this
script takes close to an hour to finish running, and this utility is an
alternative to simply fix the paths in both the files, given access to the
assets directory containing these files.
"""
import json
from pathlib import Path

from rubrix import pathfinder


def fix_index(index_path, emb_path):
	"""Fix path to image and embedding .npy files in inverse image index
	and image embedding index respectively.

	Arguments:
	----------
		index_path (pathlib.Path):
			Absolute path to inverse image index file.
		emb_path (pathlib.Path):
			Absolute path to image embeddings index file.
	"""
	for path in [index_path, emb_path]:
		find_and_replace_root(path)


def find_and_replace_root(path_to_index):
	"""Finds and replaces path to ``rubrix`` root in the corresponding
	index file.

	Arguments:
	----------
		path_to_index (pathlib.Path):
			Absolute path to index file.
	"""
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
