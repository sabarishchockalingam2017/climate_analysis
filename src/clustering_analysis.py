from config.main_config import PROJECT_HOME, RESP19_PATH, DATA_PATH
import pandas as pd
import src.helpers.data_processing as dataproc
from kmodes.kmodes import KModes
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import logging.config
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

''' Script for clustering of categorical and numerical features and outputting results to data folder'''

# disabling interactive plot output viewer
matplotlib.use('Agg')

# setting up logging
logger = logging.getLogger("clustering_analysis")

def cat_clust(citycompile):
    ''' Clustering for numerical features.
    Args:
        citycompile (Dataframe): Dataframe with CDP questionaire responses compiled at city level

    Output:
        CatClust_LPlot.jpg: plot of error vs number of clusters to find elbow (best number of clusters).
        catclustresults.csv: csv file saved to data path with clustering results.
    '''
    # get categorical variables and try various number of clusters
    citycatvars = citycompile.select_dtypes(include='object')
    catcols = citycatvars.columns
    cost = []
    for num_clusters in list(range(1, 6)):
        kmode = KModes(n_clusters=num_clusters, init="Cao", n_init=1)
        kmode.fit_predict(citycatvars)
        cost.append(kmode.cost_)

    # plot error vs clusters
    y = np.array([i for i in range(1, 6, 1)])
    catlplot = plt.plot(y, cost);
    plt.title('Cost vs Number of Clusters');
    plt.xlabel('Clusters');
    plt.ylabel('Cost');
    plt.savefig(Path(DATA_PATH, 'CatClust_Lplot.jpg'));

    citycatvars = citycompile.select_dtypes(include='object')
    catcols = citycatvars.columns

    # define the k-modes model
    km = KModes(n_clusters=3,
                init='Cao', n_init=11)

    # fit the clusters to the skills dataframe
    clusters = km.fit_predict(citycatvars)

    # get an array of cluster modes
    kmodes = km.cluster_centroids_
    shape = kmodes.shape

    clustdf = pd.DataFrame(data=kmodes, columns=catcols)
    clustdf.to_csv(Path(DATA_PATH,'catclustresults.csv'))

def num_clust(citycompile):
    ''' Clustering for numerical features.
    Args:
        citycompile (Dataframe): Dataframe with CDP questionaire responses compiled at city level

    Output:
        NumClust_LPlot.jpg: plot of error vs number of clusters to find elbow (best number of clusters).
        numclustresults.csv: csv file saved to data path with clustering results.
    '''

    # scaling numerical features
    citynumvars = citycompile.select_dtypes(exclude='object')
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(citynumvars)

    kmeans_kwargs = {"init": "random",
                     "n_init": 10,
                     "max_iter": 300,
                     "random_state": 42,
                     }
    # finding appropriate number of clusters
    sse = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(scaled_features)
        sse.append(kmeans.inertia_)

    # plot error vs number of clusters
    numlplot = plt.plot(range(1, 11), sse);
    plt.title('SSE vs Number of Clusters');
    plt.xticks(range(1, 11));
    plt.xlabel("Number of Clusters");
    plt.ylabel("SSE");
    plt.savefig(Path(DATA_PATH, 'NumClust_Lplot.jpg'));

    kmeans = KMeans(n_clusters=2, **kmeans_kwargs)
    kmeans.fit(scaled_features)
    sse.append(kmeans.inertia_)

    clustdf = pd.DataFrame(kmeans.cluster_centers_, columns=citynumvars.columns)
    clustdf.to_csv(Path(DATA_PATH,'numclustresults.csv'))

def run_clustering(args=None):
    ''' Processes data and ouputs clustering analysis results. '''
    respdata = pd.read_csv(RESP19_PATH)
    # compile at city level
    unimpcitycomp = dataproc.compile_at_city(respdata)
    # impute data
    citycomp = dataproc.impute_data(unimpcitycomp)

    # clustering categorical variables
    cat_clust(citycomp)

    # clustering numerical variables
    num_clust(citycomp)

    logger.info("Clustering complete.")


if __name__ == "__main__":
    run_clustering()