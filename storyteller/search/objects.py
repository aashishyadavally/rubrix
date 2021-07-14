"""Detects objects from all the images in the data directory to create
an keyword-image index, thus enabling object-based image filtering for
keyword/phrase based image retrieval.

References:
-----------
This script is an extension of app/ai.py and app/main.py at
`https://github.com/organization-x/cv-yolo-scaffold/`
"""
import json
import argparse
from pathlib import Path

import cv2

import numpy as np

from tqdm import tqdm

from storyteller import pathfinder


def get_yolo_net(cfg_path, weights_path):
    """Loads pretrained YOLOv4 model.

    Arguments:
    ----------
        cfg_path (pathlib.Path):
            Path to darknet configuration file.
        weights_path (pathlib.Path):
            Path to YOLOv4 weights.

    Returns:
    --------
        net (cv2.dnn.Net):
            Pretrained YOLOv4 model.
    """

    if not cfg_path or not weights_path:
        raise Exception('Missing inputs. See file.')

    print('[INFO] Loading YOLOv4 net from disk.')
    net = cv2.dnn.readNetFromDarknet(str(cfg_path), str(weights_path))

    return net


def get_labels(names_path):
    """Loads object labels from .names file in darknet/data.

    Arguments:
    ----------
        names_path (pathlib.Path):
            Path to .names file in darknet/data.

    Returns:
    --------
        labels (list):
            Labels.
    """
    with open(names_path, 'r') as file:
        labels = file.readlines()
    labels = [label.strip() for label in labels]

    return labels


def detect_objects(net, labels, image, confidence_threshold):
    """Detect objects in `image` by forwarding data through the network.

    Arguments:
    ----------
        net (cv2.dnn.Net):
            Pretrained YOLOv4 model.
        labels (list):
            Labels.
        image (numpy.ndarray):
            Image.
        confidence_threshold (float):
            Threshold for determining bounding box consideration.

    Returns:
    --------
        objects (set):
            Set of objects in the image.
    """
    # Determine only the *output* layer names that we need from YOLOv4.
    layer_names = net.getLayerNames()
    layer_names = [layer_names[pos[0] - 1] for pos in net.getUnconnectedOutLayers()]

    # Construct a blob from the input image.
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)

    # Extract layer outputs from forward pass for the input image.
    net.setInput(blob)
    layer_outputs = net.forward(layer_names)

    class_ids = []
    for output in layer_outputs:
        for detection in output:
            # Extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Filter out weak predictions.
            if confidence > confidence_threshold:
                class_ids.append(class_id)

    objects = set([labels[i] for i in class_ids])

    return objects


def create_index(images_path, weights_path, cfg_path, names_path, thresh):
    """Creates an image index mapping objects in ``names_path`` to image files
    containing the object. JSON file is written to /assets directory.

    Arguments:
    ----------
        images_path (pathlib.Path):
            Path to images directory.
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
    image_paths = list(images_path.iterdir())
    index = dict(zip(labels, [[] for _ in range(len(labels))]))

    for _id in tqdm(range(len(image_paths))):
        image_path = image_paths[_id]
        image = cv2.imread(str(image_path))
        objects = detect_objects(net, labels, image, thresh)

        for object in objects:
            _paths = index[object]
            _paths.append(str(image_path))
            index[object] = _paths

    index_path = pathfinder.get('storyteller', 'assets', 'index.json')

    with open(index_path, 'w') as index_file:
        json.dump(index, index_file, indent=4)

    print('[INFO] Index creation successful.')
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create image index.')
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
        images_path = pathfinder.get('storyteller', 'assets', 'data',
                                     'images', 'val')
    else:
        images_path = Path(args.images_path)

    if args.weights_path is None:
        weights_path = pathfinder.get('storyteller', 'assets', 'models',
                                      'yolov4.weights')
    else:
        weights_path = Path(args.weights_path)

    if args.cfg_path is None:
        cfg_path = pathfinder.get('storyteller', 'search', 'darknet',
                                  'cfg', 'yolov4.cfg')
    else:
        cfg_path = Path(args.cfg_path)

    if args.names_path is None:
        names_path = pathfinder.get('storyteller', 'search', 'darknet',
                                     'data', 'coco.names')
    else:
        names_path = Path(args.names_path)


    create_index(images_path, weights_path, cfg_path, names_path,
                 args.confidence_threshold)
