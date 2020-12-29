import argparse
import logging.config
from config.main_config import LOGGING_PATH, LOGGING_CONFIG
from app.app import app
from src.clustering_analysis import run_clustering

''' This is a central location to run all files.'''

logging.config.fileConfig(LOGGING_CONFIG,
                          disable_existing_loggers=False,
                          defaults={'log_dir': LOGGING_PATH})
logger = logging.getLogger("run_climate_analysis")

def run_app():
    'Boots up app on server.'
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'])

if __name__=='__main__':

    parser = argparse.ArgumentParser(description="Run app or source code")

    subparsers = parser.add_subparsers()

    # Sub-parser for running clustering
    sb_clust = subparsers.add_parser("run_clustering",
                                     description="Runs clustering analysis and outputs to data folder." )
    sb_clust.set_defaults(func=run_clustering)

    args = parser.parse_args()

    # if run_clustering passed, run clustering only
    if hasattr(args, 'func'):
        args.func(args)
    else:
        run_app()
