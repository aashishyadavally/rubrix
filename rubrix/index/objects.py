"""Creates an inverse-image index mapping the list of objects in the .names
file in darknet/data directory to the images in the data directory that
contain each of these objects.

The inverse-image index file facilitates an object-based image filtering
for keyword/phrase based image retrieval.
"""
import json
import argparse
from pathlib import Path

import cv2

from tqdm import tqdm

from rubrix import pathfinder
from rubrix.image.detect import get_yolo_net, get_labels, detect_objects


def create_index(images_path, weights_path, cfg_path, names_path, thresh):
    """Creates an image index mapping objects in ``names_path`` to image
    files containing the object. JSON file is written to /assets directory.

    Arguments:
    ----------
        images_path (pathlib.Path or list of pathlib.Path):
            Path to images directory / List of paths to multiple image
            directories.
        weights_path (pathlib.Path):
            Path to YOLOv4 pretrained weights file.
        cfg_path (pathlib.Path):
            Path to darknet configuration file.
        names_path (pathlib.Path):
            Path to darknet names file.
        thresh (float):
            Confidence level threshold.
    """
    # Retrieve YOLOv4 model related variables to detect objects in an image.
    net = get_yolo_net(cfg_path, weights_path)
    labels = get_labels(names_path)

    image_paths = []
    if isinstance(images_path, Path):
        image_paths = list(images_path.iterdir())
    elif isinstance(images_path, list):
        image_paths = []
        for paths in images_path:
            image_paths += list(paths.iterdir())

    index = dict(zip(labels, [[] for _ in range(len(labels))]))

    for _id in tqdm(range(len(image_paths))):
        image_path = image_paths[_id]
        image = cv2.imread(str(image_path))
        objects = detect_objects(net, labels, image, thresh)

        for object in objects:
            _paths = index[object]
            _paths.append(str(image_path))
            index[object] = _paths

    index_path = pathfinder.get('assets', 'index.json')

    with open(index_path, 'w') as index_file:
        json.dump(index, index_file, indent=4)

    print('[INFO] Index creation successful.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create inverse image index.')
    parser.add_argument('--images', dest='images_path', type=str,
                        help='Path to images directory.')
    parser.add_argument('--weights', dest='weights_path', type=str,
                        help='Path to YOLOv4 weights.')
    parser.add_argument('--cfg', dest='cfg_path', type=str,
                        help='Path to darknet configuration file.')
    parser.add_argument('--names', dest='names_path', type=str,
                        help='Path to darknet names file.')
    parser.add_argument('--thresh', dest='confidence_threshold', type=float,
                        default=0.5, help='Confidence threshold.')

    args = parser.parse_args()

    if args.images_path is None:
        images_path = [
            pathfinder.get('assets', 'data', 'train'),
            pathfinder.get('assets', 'data', 'val'),
        ]
    else:
        images_path = Path(args.images_path)

    if args.weights_path is None:
        weights_path = pathfinder.get('assets', 'models', 'yolov4.weights')
    else:
        weights_path = Path(args.weights_path)

    if args.cfg_path is None:
        cfg_path = pathfinder.get('rubrix', 'index', 'darknet',
                                  'cfg', 'yolov4.cfg')
    else:
        cfg_path = Path(args.cfg_path)

    if args.names_path is None:
        names_path = pathfinder.get('rubrix', 'index', 'darknet',
                                    'data', 'coco.names')
    else:
        names_path = Path(args.names_path)

    create_index(images_path, weights_path, cfg_path, names_path,
                 args.confidence_threshold)
