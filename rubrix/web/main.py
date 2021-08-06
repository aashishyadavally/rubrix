"""TODO: This script is incomplete/experimental. In its current form, the Flask app
redirects to results page before the query is executed, resulting in an error.

Possible alternative is to move to FastAPI or to integrate Flask app with celery.
"""

# Eun by typing python3 main.py in a terminal 
import os
import sys
import json
import shutil

from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, render_template, make_response
from flask import send_from_directory

import tensorflow_hub as hub

from rubrix
from rubrix.search.encodings import MODULE_URL
from rubrix.web.query import query_by_text


MODEL = hub.load(MODULE_URL)


# Setup the webserver
# This is required when using coding center
def get_base_url(port):
    info = json.load(open(os.path.join(os.environ['HOME'], ".smc", "info.json"), 'r'))
    project_id = info['project_id']
    base_url = "/%s/port/%s/" % (project_id, port)
    return base_url

def allowed_file(filename, ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg'])):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


port =13459
base_url = get_base_url(port)
app = Flask(__name__, static_url_path=base_url+'static')
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024


@app.route(base_url)
def search():
    print('In search page')
    return render_template('Search.html')


@app.route(base_url, methods=['POST'])
def search_post():
    prompt = request.form['prompt']
    print(f'Printing from search_post: {prompt}')

    retrieved_images = query_by_text(prompt, MODEL)
    dst_path = pathfinder.get('rubrix', 'web', 'static', 'predictions')
    print(dst_path)
    if dst_path.is_dir():
        shutil.rmtree(dst_path)

    data = {}    
    for idx, image in enumerate(retrieved_images):
        data[f'prediction{idx}'] = str(image)

        print(str(dst_path / f'{idx}.png'))
        try:
            shutil.copyfile(str(image), str(dst_path / f'{idx}.png'))
        except Exception as e:
            print(e)

    return redirect(url_for('results', data=data))


@app.route(base_url + '/reverse-search')
def reverse_search():
    return render_template('Reverse-Search.html')


@app.route(base_url + '/reverse-search', methods=['POST'])
def reverse_search_post():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('results', filename=filename))


if __name__ == "__main__":
    '''
    coding center code
    '''
    website_url = 'cocalc2.ai-camp.org'
    print(f"Try to open\n\n    https://{website_url}" + base_url + '\n\n')
    # remove debug=True when deploying it
    app.run(host = '0.0.0.0', port=port, debug=True, threaded=True)
    sys.exit(0)
