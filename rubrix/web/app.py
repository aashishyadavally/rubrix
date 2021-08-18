"""Entry-point for running web application. Useful to launch simple web
application using Flask.

Launch web application by typing ``python3 app.py`` in a terminal.
"""
import os
# Forcing web application to run on CPU.
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import sys
import json
import shutil
from pathlib import Path

from werkzeug.utils import secure_filename
from flask import (Flask, flash, request, redirect, url_for, render_template,
                   make_response, send_from_directory)

import tensorflow_hub as hub

from rubrix import pathfinder
from rubrix.index.encodings import MODULE_URL
from rubrix.query import query_by_text, query_by_image_objects


# Load Universal Sentence Encoder. Building the TF graph takes time
# and this operation on the first run is time intensive.
MODEL = hub.load(MODULE_URL)

# Port number to run Flask app on
PORT = 8000

# Directory to save user-uploaded images
UPLOAD_FOLDER = 'uploads'

# Possible image extensions for user-uploaded file.
ALLOWED_EXTENSIONS=set(['.png', '.jpg', '.jpeg'])

# Flask app set-up configuration
app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024


def allowed_file(filename):
    """Checks if the user-uploaded file has a valid extension.

    Arguments:
    ----------
        filename (str):
            Name of user-uploaded file

    Returns:
    --------
        (bool):
            True, if valid file.
            False, otherwise.
    """
    extension = Path(filename).suffix.lower()
    if extension in ALLOWED_EXTENSIONS:
        return True
    return False


def copy_results(images):
    """Copies retrieved images from image database to 
    ``rubrix/web/static/predictions``. File names of the retrieved images
    is returned.

    Arguments:
    ----------
        images (list):
            List of :class: ``pathlib.Path`` objects for the retrieved images.

    Returns:
    --------
        image_names (list):
            List of names of retrieved images.
    """
    image_names = [Path(image).name for image in images]
    dst_path = pathfinder.get('rubrix', 'web', 'static', 'predictions')
    if not dst_path.is_dir():
        dst_path.mkdir(parents=True)

    for idx, image in enumerate(images):
        try:
            shutil.copyfile(str(image), str(dst_path / image_names[idx]))
        except Exception as e:
            print(e)
    return image_names


def get_yolo_paths():
    """Extracts paths of darknet YOLOv4 objects, needed for object detection.

    Returns:
    --------
        (tuple):
            Tuple of :class: ``pathlib.Path`` objects corresponding to the
            weights location, configuration file location and object names
            location.
    """
    weights_path = pathfinder.get('assets', 'models', 'yolov4.weights')
    cfg_path = pathfinder.get('rubrix', 'index', 'darknet', 'cfg',
                              'yolov4.cfg')
    names_path = pathfinder.get('rubrix', 'index', 'darknet', 'data',
                                'coco.names')

    return (weights_path, cfg_path, names_path)


@app.route('/')
def search():
    return render_template('Search.html')


@app.route('/', methods=['POST'])
def search_post():
    prompt = request.json['prompt']
    print(prompt)
    retrieved_images = query_by_text(prompt, MODEL)
    print(retrieved_images)
    if retrieved_images != []:
        image_names = copy_results(retrieved_images)
        message = f"Image search results for \"{prompt}\":"
        return redirect(url_for('results',
                                message=message,
                                result1='predictions/' + image_names[0],
                                result2='predictions/' + image_names[1],
                                result3='predictions/' + image_names[2],
                                result4='predictions/' + image_names[3],
                                result5='predictions/' + image_names[4]
                                ))
    else:
        return redirect(url_for('search'))


@app.route('/reverse-search')
def reverse_search():
    return render_template('Reverse-Search.html')


@app.route('/reverse-search', methods=['POST'])
def reverse_search_post():
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploads_dir = pathfinder.get('rubrix', 'web') / UPLOAD_FOLDER
        # Create ``UPLOAD_FOLDER`` if not already exists.
        if not uploads_dir.is_dir():
            uploads_dir.mkdir(parents=True)
        # Save uploaded file to ``UPLOAD_FOLDER``.
        file.save(str(uploads_dir / filename))

    image_path = uploads_dir / filename
    _paths = get_yolo_paths()

    retrieved_images = query_by_image_objects(image_path, *_paths)

    if retrieved_images != []:
        image_names = copy_results(retrieved_images)
        return redirect(url_for('results',
                                message='Reverse-image-search results:',
                                result1='predictions/' + image_names[0],
                                result2='predictions/' + image_names[1],
                                result3='predictions/' + image_names[2],
                                result4='predictions/' + image_names[3],
                                result5='predictions/' + image_names[4]
                                ))
    else:
        return redirect(url_for('search'))


@app.route('/results')
def results(message=None, result1=None, result2=None, result3=None,
            result4=None, result5=None):
    return render_template('Results.html',
                            message=request.args.get('message'),
                            result1=request.args.get('result1'),
                            result2=request.args.get('result2'),
                            result3=request.args.get('result3'),
                            result4=request.args.get('result4'),
                            result5=request.args.get('result5'))


if __name__ == "__main__":
    app.run(host='localhost', port=PORT, debug=True, threaded=True)
    sys.exit(0)
