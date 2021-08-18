"""2048-dimension feature vectors describing the images are extracted using
:method: ``rubrix.images.extract_image_descriptors`` for all the images in
the image database. These are saved in assets/data/descriptors directory.
"""
import argparse
from pathlib import Path

from tqdm import tqdm

import numpy as np

from rubrix import pathfinder
from rubrix.image.extract import extract_image_descriptors


TARGET_SIZE = (299, 299)


def save_image_descriptors(images_path):
    """Creates an index mapping cluster labels to corresponding image keys
    and 512 dimension image descriptor .npy arrays.

    Arguments:
    ----------
        images_path (pathlib.Path or list of pathlib.Path):
            Path to images directory / List of paths to multiple image
            directories.
    """
    image_paths = []
    if isinstance(images_path, Path):
        image_paths = list(images_path.iterdir())
    elif isinstance(images_path, list):
        image_paths = []
        for paths in images_path:
            image_paths += list(paths.iterdir())
    X = []
    descriptors_path = pathfinder.get('assets', 'data', 'descriptors')
    descriptors_path.mkdir(exist_ok=True)

    print("[INFO] Extracting and saving image descriptors.")
    for path in tqdm(image_paths):
        array = extract_image_descriptors(path, 'inception', TARGET_SIZE)
        np.save(descriptors_path / f'{path.stem}.npy', array)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create inverse image index.')
    parser.add_argument('--images', dest='images_path', type=str,
                        help='Path to images directory.')
    args = parser.parse_args()

    if args.images_path is None:
        images_path = [
            pathfinder.get('assets', 'data', 'train'),
            pathfinder.get('assets', 'data', 'val'),
        ]
    else:
        images_path = Path(args.images_path)

    save_image_descriptors(images_path)
