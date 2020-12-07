import logging
from config.main_config import LOGGING_PATH, LOGGING_CONFIG

''' This is a central location to run all files.'''

logging.config.fileConfig(LOGGING_CONFIG,
                          disable_existing_loggers=False,
                          defaults={'log_dir': LOGGING_PATH})
logger = logging.getLogger("run_climate_analysis")

def run_app():
    'Boots up app on server.'
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'])

if __name__=='__main__':
    run_app()
