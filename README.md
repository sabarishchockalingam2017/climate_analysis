# Climate Analysis App Repository

- [Project Description](#project-description)
- [Repo structure](#repo-structure)
- [Setup](#setup)
  * [1. Set up environment](#1-set-up-environment)
    + [With `virtualenv` and `pip`](#with-virtualenv-and-pip)
    + [With `conda`](#with-conda)
  * [2. Download data ](#2-download-and-upload-data)
  * [3. Perform Clustering ](#3-perform-clustering)
- [Run the application](#run-the-application)

## Project Description
A Flask app presenting my analysis of the Carbon Disclosure Project's data (hosted on Kaggle). Goals are to 
to mine for insights and devise KPIs for better assessing problems arising from climate change.

## Repo structure 

```
├── README.md                         <- You are here
│
├── app
│   ├── static/                       <- CSS, JS files that remain static
│       ├── main.css                  <- CSS formatting parameters for app
│       ├── images/                   <- Directory to store images to be posted in Flask web UI
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│       ├── home.html                 <- Main page with app
│       ├── layout.html               <- Base layout followed by all other pages
│   ├── app.py                        <- Flask app's main .py file
│
├── config                            <- Directory for configurations files (yaml, py, conf, etc.) to control app and set parameters
│   ├── logging/                      <- Configuration files for python loggers
│   ├── flask_config.py               <- Settings for flask app
│   ├── main_config.py                <- Settings for other items such as model storage directory and data directory
│
├── data                              <- Folder that contains data used or generated. Extract CDP data file here.
│
├── logs                              <- Directory holds logs created by logger files.
│
├── notebooks                         <- For notebooks containing rough data analysis.
│
├── src                               <- Source data for the project 
│   ├── helpers/                      <- Helper scripts used in main src files 
│   ├── cluster_analysis.py           <- Run script to perform clustering and output cluster defining values.
│
├── viusals/                          <- Called in Flask app to create interactive plotly graph objects.
│
├── Procfile                          <- Used by gunicorn to deploy app on heroku.
├── requirements.txt                  <- Python package dependencies 
├── run.py                            <- Run to start up flask app
├── runtime.txt                       <- Sets python version to be used by heroku.
```
This project structure was partially influenced by the [Cookiecutter Data Science project](https://drivendata.github.io/cookiecutter-data-science/).

## Setup
### 1. Setup Environment
Make sure to have virtualenv or conda installed.

#### With `virtualenv`
```bash
pip install virtualenv

virtualenv climate_analysis

source climate_analysis/bin/activate

pip install -r requirements.txt

```
#### With `conda`

```bash
conda create -n climate_analysis python=3.7
conda activate climate_analysis
pip install -r requirements.txt

```

### 2. Download data

Download the CDP data set from: https://www.kaggle.com/c/cdp-unlocking-climate-solutions/data.

Extract the data set file into the data directory.

### 3. Perform Clustering
Run the following command from the projects home directory.
```bash
python run.py run_clustering
```

## Run the application
Run the following command from the projects home directory.
```bash
python run.py
```