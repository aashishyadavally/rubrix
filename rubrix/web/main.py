# run by typing python3 main.py in a terminal 
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, render_template
from flask import send_from_directory

# setup the webserver

# this is required when using coding center
def get_base_url(port):
    info = json.load(open(os.path.join(os.environ['HOME'], ".smc", "info.json"), 'r'))
    project_id = info['project_id']
    base_url = "/%s/port/%s/" % (project_id, port)
    return base_url

port = 12350
base_url = get_base_url(port)
app = Flask(__name__, static_url_path=base_url+'static')

@app.route(base_url)
def home():
    return render_template('Search.html')

@app.route('/', methods=['POST'])
def home_post():
    # check if the post request has the file part
    pass

@app.route('/uploads/<filename>', methods=['POST', 'GET'])
def results(filename):
    pass

@app.route('/files/<path:filename>')
def files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    '''
    coding center code
    '''
    website_url = 'cocalc2.ai-camp.org'
    # remove debug=True when deploying it
    app.run(host = '0.0.0.0')
    import sys; sys.exit(0)
