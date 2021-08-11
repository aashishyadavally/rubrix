"""Extracts features from an image based on pretrained models such as
Inception V3, VGG19 and ResNet50.
"""
import numpy as np

import tensorflow
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input as inception_preprocess_input
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.applications.vgg19 import preprocess_input as vgg19_preprocess_input
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess_input


def extract_image_descriptors(path_to_image, model_name, target_size):
    """Encodes an image as a numpy array, based on the image descriptors
    as extracted by the deep CNN model architecture.

    Arguments:
    ----------
        path_to_image (pathlib.Path):
            Path to input image.
        model_name (str):
            Key for instantiating CNN model architecture.
        target_size (tuple):
            Tuple of integers, dimensions to resize input images to.

    Returns:
    --------
        id_array (numpy.ndarray):
            Image descriptor array.
    """
    preprocess_input = None

    if model_name == 'inception':
        # Keras seems to return mixed_10 layer output and not of
        # pool_3 layer if ``pooling`` parameter is not set to 'avg'.
        model = InceptionV3(include_top=False, pooling='avg')
        preprocess_input = inception_preprocess_input
    elif model_name == 'vgg16':
        model = VGG19(include_top=False)
        preprocess_input = vgg19_preprocess_input
    elif model_name == 'resnet50':
        model = ResNet50(include_top=False)
        preprocess_input = resnet_preprocess_input

    img = image.load_img(path_to_image, target_size=target_size)
    array = image.img_to_array(img)
    array = np.expand_dims(array, axis=0)
    array = preprocess_input(array)
 
    # Using model(x) instead of model.predict(x) here.
    # This ensures that excessive number of tracings (an expensive
    # operation) are avoided.
    id_array = model(array).numpy()
    id_array = id_array.reshape(-1)

    return id_array
