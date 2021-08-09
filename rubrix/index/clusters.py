"""Creates an index mapping cluster labels to corresponding image keys
and 512 dimension image descriptor .npy arrays.

Feature vectors describing the images are extracted using :method:
``rubrix.images.extract_image_descriptors``. Furthermore, PCA based
dimensionality reduction is performed to reduce the number of dimensions
to ``IMAGE_OUTPUT_DIM`` (512 by default).

Using :class: ``ElbowMethodVisualizer``, it was determined that dividing
the image descriptor arrays into 60 clusters was optimal.
"""
import json
import pickle
import operator
import argparse
from pathlib import Path

from tqdm import tqdm

import numpy as np

from scipy.spatial.distance import cdist

import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from rubrix import pathfinder
from rubrix.config import K_RANGE, TARGET_SIZE, IMAGE_OUTPUT_DIM
from rubrix.images.extract import extract_image_descriptors
from rubrix.utils import dot_product


class ElbowMethodVisualizer:
    """Implements Elbow Method to help determine the optimal number of
    clusters by fitting the model with a range of values of K.
    """
    def __init__(self, k_range):
        """Initializes :class: ``ElbowMethodVisualizer``.

        Arguments:
        ----------
            k_range (tuple):
                Range of values of K for Elbow Method.
        """
        self.k_range = range(*k_range)
        self.distortions = None
        self.inertia = None

    def fit(self, X):
        """Fits multiple kMeans clustering models for K in :attr: ``k_range``.
        Metrics such as distortion and inertia are computed for each value
        of K.

        Arguments:
        ----------
            X (numpy.ndarray):
                Input data.
        """
        distortions, inertia = [], []

        for k in self.k_range:
            model = KMeans(n_clusters=k)
            model.fit(X)

            distortion = sum(np.min(cdist(X, model.cluster_centers_,
                                         'euclidean'), axis=1)) / X.shape[0]
            distortions.append(distortion)
            inertia.append(model.inertia_)

        self.distortions, self.inertia = distortions, inertia
        return self

    def plot(self):
        """Plots elbow method using distortion and inertia to help
        determine the optimal value of K.
        """
        fig, ax = plt.subplots(nrows=2, ncols=1)

        ax[0].plot(self.k_range, self.distortions)
        ax[0].set_title('Elbow method using Distortion')
        ax[0].set_xlabel('k')
        ax[0].set_ylabel('Distortion')

        ax[1].plot(self.k_range, self.inertia)
        ax[1].set_title('Elbow method using Inertia')
        ax[1].set_xlabel('k')
        ax[1].set_ylabel('Inertia')

        path = pathfinder.get('assets', 'elbow_method.png')
        fig.savefig(path)


def create_clusters_index(images_path):
    """Creates an index mapping cluster labels to corresponding image keys
    and 512 dimension image descriptor .npy arrays.

    Arguments:
    ----------
        images_path (pathlib.Path or list of pathlib.Path):
            Path to images directory / List of paths to multiple image
            directories.
    image_paths = []
    if isinstance(images_path, Path):
        image_paths = list(images_path.iterdir())
    elif isinstance(images_path, list):
        image_paths = []
        for paths in images_path:
            image_paths += list(paths.iterdir())
    """
    X = []
    descriptors_path = pathfinder.get('assets', 'data', 'descriptors')
    descriptors_path.mkdir(exist_ok=True)

    print("[INFO] Extracting image descriptors.")
    for path in tqdm(image_paths):
        array = extract_image_descriptors(path, 'inception', TARGET_SIZE)
        X.append(array)

    X = np.asarray(X)
    print("[INFO] Saving scaled features' mean and standard deviation.")
    scaler_path = pathfinder.get('assets', 'scaler')
    scaler_path.mkdir(exist_ok=True)
    mu, sigma = np.mean(X), np.std(X)
    np.save(scaler_path / 'mean.npy', mu)
    np.save(scaler_path / 'std.npy', sigma)
    X = (X - mu) / sigma

    print("[INFO] Reducing dimensionality of image descriptors.")
    pca = PCA(n_components=IMAGE_OUTPUT_DIM).fit(X)
    model_path = pathfinder.get('assets', 'models', 'pca_model.pkl')
    with open(model_path, 'wb') as pickle_file:
        pickle.dump(pca, pickle_file)
    X_reduced = pca.transform(X)

    for i, path in enumerate(image_paths):
        x = X_reduced[i]
        np.save(descriptors_path / f'{path.stem}.npy', x)

    paths_to_image_descriptors = list(descriptors_path.iterdir())

    # Comment all lines in this function before this, and uncomment the
    # next three lines to avoid creating image descriptors, if already done.
#    descriptors_path = pathfinder.get('assets', 'data', 'descriptors')    
#    paths_to_image_descriptors = list(descriptors_path.iterdir())
#    X_reduced = [np.load(path) for path in paths_to_image_descriptors]

    model = KMeans(n_clusters=60)
    model.fit(X_reduced)
    cluster_centers = model.cluster_centers_

    cluster_centers_path = pathfinder.get('assets', 'data', 'cluster_centers')
    cluster_centers_path.mkdir(exist_ok=True)

    for idx, cluster_center in enumerate(cluster_centers):
        np.save(cluster_centers_path / f'cluster{idx}.npy', cluster_center)

    index = dict(zip([f'cluster{i}' for i in range(len(cluster_centers))],
                     [[] for _ in range(len(cluster_centers))]))

    # If the K-Means algorithm stops before fully converging (depending on
    # the ``tol`` and ``max_iter`` parameters), these will not be consistent
    # with labels_.
    # Manually calculating labels for the images in the dataset.
    train_path = pathfinder.get('assets', 'data', 'train')
    val_path = pathfinder.get('assets', 'data', 'val')
    train_names = [path.stem for path in train_path.iterdir()]
    val_names = [path.stem for path in val_path.iterdir()]

    for idx in tqdm(range(len(X_reduced))):
        array = X_reduced[idx]
        label, value = max(enumerate([dot_product(array, other) \
                                      for other in cluster_centers]),
                           key=operator.itemgetter(1))
        name_stem = paths_to_image_descriptors[idx].stem
        _dict = {
            'filename': name_stem,
            'path_to_array': str(paths_to_image_descriptors[idx])
        }
        if name_stem in train_names:
            _dict['path_to_image'] = str(train_path / f'{name_stem}.jpg')
        elif name_stem in val_names:
            _dict['path_to_image'] = str(val_path / f'{name_stem}.jpg')

        index[f'cluster{label}'].append(_dict)

    index_file_path = pathfinder.get('assets', 'cluster_index.json')
    with open(index_file_path, 'w') as json_file:
        json.dump(index, json_file, indent=4)


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

    create_clusters_index(images_path)
