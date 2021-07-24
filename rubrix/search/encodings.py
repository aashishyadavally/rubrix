"""Accesses the Universal Sentence Encoder to get sentence level embeddings
and saves them as numpy files for the text captions corresponding to the
images in the dataset.
"""
import json
import argparse
from pathlib import Path

import numpy as np

import tensorflow_hub as hub

from tqdm import tqdm

from rubrix import pathfinder


# Tensorflow hub link for Universal Sentence Encoder (large).
MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-large/5"


def embedd_captions(model, captions_path, this_embeddings_folder):
    """
    Encodes all the captions in a JSON file at `captions_path` into separate
    .npy files and returns a dictionary mapping image identifiers to
    paths of corresponding sentence embedding files.

    Arguments:
    ----------
        model (tensorflow.saved_model):
            Universal sentence encoder (large) tensorflow saved model.
        captions_path (pathlib.Path or list of pathlib.Path objects):
            Path to the captions JSON file / List of paths to multiple
            captions JSON files.
        this_embeddings_folder (string):
            Path to the folder to store .npy files corresponding to the
            sentence embeddings.

    Returns:
    --------
        ids_to_numpy_paths (dict):
            ids_to_numpy_paths[image_id] -> a list of the absolute paths
            of the numpy embeddings of all captions of image_id
    """
    # Initialize the output
    ids_to_numpy_paths = {}

    # Load in the data
    ids_captions = []

    if isinstance(captions_path, Path):
        with open(captions_path, "r") as captions_file:
            ids_captions = json.load(captions_file)["contents"]
    elif isinstance(captions_path, list):
        for path in captions_path:
            with open(path, "r") as captions_file:
                ids_captions += json.load(captions_file)["contents"]

    for _id in tqdm(range(len(ids_captions))):
        caption_pair = ids_captions[_id]
        caption = caption_pair["caption"]
        image_id = caption_pair["image_id"]

        if image_id in ids_to_numpy_paths.keys():
            # if this is not the first time the image has been embedded then
            # we need to add a "_(#Images_Already_Embedded + 1)" to the path of
            # the .npy file.
            filename = f"{image_id[:-4]}_{len(ids_to_numpy_paths[image_id]) + 1}.npy"
            numpy_path = Path(this_embeddings_folder) / filename
            ids_to_numpy_paths[image_id].append(str(numpy_path))
        else:
            # If this is the first time this image has been embedded, then _1
            numpy_path = Path(this_embeddings_folder) / f"{image_id[:-4]}_1.npy"
            ids_to_numpy_paths[image_id] = [str(numpy_path)]

        # Do the embedding
        embedd_tensor = model([caption]) # (1, 512) tensor
        embedd_numpy = embedd_tensor.numpy()[0] # (512, ) numpy array
        np.save(numpy_path, embedd_numpy)

    return ids_to_numpy_paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate sentence embeddings.")
    parser.add_argument('--captions', dest='captions_path', type=str,
                        help='Path to image captions.')

    args = parser.parse_args()

    if args.captions_path is None:
        captions_path = [
            pathfinder.get('rubrix', 'assets', 'data', 'train_captions.json'),
            pathfinder.get('rubrix', 'assets', 'data', 'val_captions.json'),
        ]
    else:
        captions_path = Path(args.captions_path)

    # Folder to store .npy files corresponding to dataset sentence embeddings.
    embeddings_folder = pathfinder.get("rubrix", "assets", "data",
                                       "embeddings")
    embeddings_folder.mkdir(exist_ok=True)

    # Loading in the large/5 model
    # MODEL( list_of_strings ) will embedd the strings in a (numstrings,512)
    # tensor.
    # TODO: Maybe change this part to load from locally stored model.
    model = hub.load(MODULE_URL)

    ids_to_paths = embedd_captions(model, captions_path, embeddings_folder)

    json_embedding_location = pathfinder.get("rubrix", "assets",
                                             "imageEmbeddingLocations.json")

    with open(json_embedding_location, 'w') as embedding_file:
        json.dump(ids_to_paths, embedding_file, indent=4)
