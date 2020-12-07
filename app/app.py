from flask import Flask, render_template, url_for, flash
import logging
import logging.config
from config.main_config import LOGGING_PATH, LOGGING_CONFIG
import os
import app.helpers.prediction_handler as predhand

'''This is the flask app and builds the webpage interface for the analysis.'''

app = Flask(__name__)
app.config.from_object('config.flask_config')


logger = logging.getLogger("app")


@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    return render_template('home.html',
                           title='Home')

@app.context_processor
def override_url_for():
    ''' New CSS is not udpated due to browser cache. This function appends time to css path to make the updated CSS seem
    like a new file. '''
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    ''' This function appends the date to the css path'''
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
