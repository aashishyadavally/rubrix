"""Detects objects from an image using the YOLOv4 algorithm.

References:
-----------
This script is an extension of app/ai.py and app/main.py at
`https://github.com/organization-x/cv-yolo-scaffold/`
"""
import cv2

import numpy as np


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

