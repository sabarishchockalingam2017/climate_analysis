from flask import Flask, render_template, url_for, flash
import logging
import logging.config
from config.main_config import CITIES19_PATH, RESP19_PATH
import os
import pandas as pd
import visuals as viz

'''This is the flask app and builds the webpage interface for the analysis.'''

app = Flask(__name__)
app.config.from_object('config.flask_config')


logger = logging.getLogger("app")

# loading city and response data from 2019 for analysis and visualization
cities19 = pd.read_csv(CITIES19_PATH)
resp19 = pd.read_csv(RESP19_PATH)

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():

    # world map showing reporting cities
    worldmap = viz.create_worldmap(cities19)

    # hazard to demographic sankey plot
    hazdemosankey = viz.create_sankey(resp19)

    # bar chart counting cities with vulnerability assessments
    vulassesplot = viz.create_vulassesbar(resp19)

    # bar chart counting number of times hazards are listed and their
    # expected probability
    hazbarplot = viz.create_hazbarplot(resp19)

    # bar charting show adaptataion steps and number of cities undertaking them
    adapbarplot = viz.create_adaptplot(resp19)

    # bar chart showing factors affecting adaptation
    adfactbarplot = viz.create_adaptfactorsplot(resp19)

    return render_template('home.html',
                           sankeyplot=hazdemosankey,
                           worldplot=worldmap,
                           vulplot=vulassesplot,
                           hazplot=hazbarplot,
                           adapplot=adapbarplot,
                           adaptfactorsplot=adfactbarplot
                           )

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
