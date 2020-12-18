import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
from shapely import wkt
import json
import numpy as np
import matplotlib.colors as randcolors

''' Functions to create interactive plotly visualizations and pass on to Flask app'''

def filtq(qdf, qnum, cnum, rnum):
    '''filters CDP questionaire dataset by question, column and row number'''
    filcon = (qdf['Question Number'].apply(lambda x: x in qnum)) & (qdf['Column Number'].apply(lambda x: x in cnum)) & (qdf['Row Number'].apply(lambda x: x in rnum))
    return qdf[filcon]

def create_sankey(respdata):

    """ Creates a sankey plot matching top climate hazards to demographics.
    Args:
        respdata (Dataframe): response data from CDP questionaire

    Returns:
        vizJSON (json object): sankey plot reduced to json format to be passed onto web app ui.
    """

    ## getting top most listed hazards
    # filtering hazards and probability of hazards
    tempdf2 = respdata[(respdata['Question Number'] == '2.1') & ((respdata['Column Number'] == 1) | (respdata['Column Number'] == 3))]
    pivind = pd.MultiIndex.from_tuples(list(zip(tempdf2['Account Number'], tempdf2['Row Number'])),
                                       names=['Account Number', 'Row Number'])
    tempdf2['Pivot Index'] = pivind
    tempdf2 = tempdf2.pivot(values='Response Answer', columns='Column Name', index='Pivot Index')
    tempdf2 = tempdf2.reset_index().groupby(['Climate Hazards', 'Current probability of hazard']).count().reset_index()
    tempdf2 = tempdf2.pivot(values='Pivot Index', index='Climate Hazards', columns='Current probability of hazard')
    tempdf2 = tempdf2[
        ['High', 'Medium High', 'Medium', 'Medium Low', 'Low', 'Does not currently impact the city', 'Do not know']]
    tempdf2['Total'] = tempdf2.sum(axis=1)
    tempdf2 = tempdf2.sort_values(by='Total', ascending=False).head(16).drop(columns=['Total'])
    # top most listed hazards
    tophaz = tempdf2.index

    # matching hazards to demographic for sankey plot
    # hazards listed
    tempdf = respdata[(respdata['Question Number']=='2.1')\
                    & (respdata['Column Number']==1)]
    tempdf = tempdf[tempdf['Response Answer'].apply(lambda x: x in tophaz)]
    # specific population affected by hazard
    tempdf2 = respdata[(respdata['Question Number']=='2.1')\
           & ((respdata['Column Number']==10))]

    pivind = list(zip(tempdf['Account Number'],tempdf['Row Number']))
    pivind2 = list(zip(tempdf2['Account Number'],tempdf2['Row Number']))
    tempdf['Pivot Index'] = pivind
    tempdf2['Pivot Index'] = pivind2

    topcols = tempdf2.groupby('Response Answer').count().sort_values(by=['Account Number'],ascending=False).head(16).index
    tempdf2 = tempdf2.pivot(values='Account Number',index='Pivot Index',columns='Response Answer')

    tempdf3 = tempdf.merge(tempdf2[topcols].notna().reset_index(), left_on='Pivot Index', right_on='Pivot Index',\
              suffixes=('_left', '_right'))
    tempdf3 = tempdf3.groupby('Response Answer').sum()[topcols].loc[tophaz[0:10]]
    tempdf4 = tempdf3.reset_index().melt(id_vars=['Climate Hazards'])

    all_nodes = tempdf4['Climate Hazards'].values.tolist() + tempdf4['variable'].values.tolist()
    source_indices = [all_nodes.index(haz) for haz in tempdf4['Climate Hazards']]
    target_indices = [all_nodes.index(affpop) for affpop in tempdf4['variable']]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=1.0),
            label=all_nodes,
        ),

        link=dict(
            source=source_indices,
            target=target_indices,
            value=tempdf4.value,
        ))])

    fig.update_layout(title_text="Demographics Affected by Climate Hazards",
                      titlefont={'size':18},
                      font_size=10)

    vizJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return vizJSON


def create_worldmap(citydata):
    """ Creates world map visual showing populations of reporting cities.
    Args:
        citydata (Dataframe): city data which includes names, locations and populations

    Return:
        vizJSON = world map plot reduced to  json to be plotted in web UI
    """

    tempdf = citydata[['City', 'Country', 'Population', 'City Location']].dropna(subset=['City Location'])
    tempdf['City Location'] = tempdf['City Location'].apply(wkt.loads)

    tempdf['lon'] = tempdf['City Location'].apply(lambda point: point.x)
    tempdf['lat'] = tempdf['City Location'].apply(lambda point: point.y)

    # population 2 has nas filled with mean to prevent errors when plotting size according to population
    tempdf['Population2'] = tempdf.Population.fillna(tempdf.Population.mean())

    # adding population limit as brazils gionia population overshadows other cities
    maxpop = np.max(tempdf.Population)
    tempdf['PopLim'] = tempdf.Population2.apply(lambda x: min(x, maxpop / 100))

    tempdf['Population'] = tempdf.Population.fillna('Not Reported')
    tempdf['markertext'] = tempdf['City'] + ', ' + tempdf['Country'] + '<br>Population:' + tempdf['Population'].astype(
        'str')

    fig = go.Figure()
    scale = 500000
    fig.add_trace(go.Scattergeo(
        lon=tempdf.lon,
        lat=tempdf.lat,
        text=tempdf.markertext,
        marker=
        dict(
            size=tempdf.PopLim / scale
        )
    )
    )

    fig.update_layout(title="World Map of Reporting Cities",
                      titlefont={'size':18},
                      margin=dict(l=1, r=1, t=40, b=20),
                      font_size=10,)
    vizJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return vizJSON

def create_vulassesbar(respdata):
    """ Creates bar chart counting cities with climate change vulnerability assessments.
    Args:
        respdata (Dataframe): data with responses from cities to CDP questionaire.
    Return:
        vizJSON = bar chart plot reduced to  json to be plotted in web UI
    """

    # random colors to be assigned to bars for better visual distinction
    barcolors = [hexcolor for name, hexcolor in randcolors.cnames.items()]

    # filtering climate vulnerability assesment question
    tempdf = respdata[respdata['Question Number'] == '2.0'].groupby('Response Answer')\
                                                           .count()\
                                                           .sort_values(by=['Account Number'],
                                                                        ascending=False)['Account Number']
    tempdf = pd.DataFrame(tempdf).reset_index()
    tempdf.columns = ['Response', 'Number of Cities']
    fig = px.bar(tempdf, x='Number of Cities', y='Response', orientation='h',
                 color='Response')

    fig.update_layout(showlegend=False,
                      title='Climate Change Vulnerability Assessments Created')

    vizJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return vizJSON


def create_hazbarplot(respdata):
    """ Creates bar chart counting cities with climate change vulnerability assessments.
    Args:
        respdata (Dataframe): data with responses from cities to CDP questionaire.
    Return:
        vizJSON = bar chart plot reduced to  json to be plotted in web UI
    """

    # Getting hazards and their count
    tempdf2 = respdata[(respdata['Question Number'] == '2.1')
                       & ((respdata['Column Number'] == 1) | (respdata['Column Number'] == 3))]
    pivind = pd.MultiIndex.from_tuples(list(zip(tempdf2['Account Number'], tempdf2['Row Number'])),
                                       names=['Account Number', 'Row Number'])
    tempdf2['Pivot Index'] = pivind
    tempdf2 = tempdf2.pivot(values='Response Answer', columns='Column Name', index='Pivot Index')
    tempdf2 = tempdf2.reset_index().groupby(['Climate Hazards', 'Current probability of hazard']).count().reset_index()
    tempdf2 = tempdf2.pivot(values='Pivot Index', index='Climate Hazards', columns='Current probability of hazard')
    tempdf2 = tempdf2[
        ['High', 'Medium High', 'Medium', 'Medium Low', 'Low', 'Does not currently impact the city', 'Do not know']]
    tempdf2['Total'] = tempdf2.sum(axis=1)
    tempdf2 = tempdf2.sort_values(by='Total', ascending=False).head(16).drop(columns=['Total'])

    # melting to match plotly input format
    tempdf3 = pd.melt(tempdf2.reset_index(), id_vars='Climate Hazards', value_vars=tempdf2.columns)
    tempdf3 = tempdf3.rename(columns={"value": "Number of Cities"})

    color_list = ['red', 'darkorange', 'orange', 'gold', 'khaki', 'lightgreen', 'lightblue']
    color_map = dict(zip(tempdf2.columns, color_list))

    fig = px.bar(tempdf3,
                 x="Number of Cities",
                 y="Climate Hazards",
                 color="Current probability of hazard",
                 color_discrete_map=color_map)

    fig.update_layout(yaxis=dict(autorange="reversed"), yaxis_title_text=None,
                      title="Most listed Climate Hazards",
                      titlefont=dict(size=18),
                      width=700, height=400,
                      font=dict(size=10))

    vizJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return vizJSON

def create_adaptplot(respdata):
    """ Creates bar chart showing most listed adaptation steps.
    Args:
        respdata (Dataframe): data with responses from cities to CDP questionaire.
    Return:
        vizJSON = bar chart plot reduced to  json to be plotted in web UI
    """

    # filtering to get adaptations listed in city responses
    adap19 = filtq(respdata, '3.0', [1, 2, 8, 10], list(range(1000)))
    pivind = pd.MultiIndex.from_tuples(list(zip(adap19['Account Number'], adap19['Row Number'])),
                                       names=['Account Number', 'Row Number'])
    adap19['Pivot Index'] = pivind
    adap19 = adap19.pivot(values='Response Answer', columns='Column Name', index='Pivot Index')
    adact19 = adap19.reset_index().groupby('Action').count().sort_values(by=['Pivot Index'], ascending=False).head(10)[
        'Pivot Index']
    adact19 = pd.DataFrame(adact19)
    adact19.columns = ['Number of Cities']
    adact19 = adact19.reset_index()

    fig = px.bar(adact19, x='Number of Cities', y='Action', color='Action')
    fig.update_layout(showlegend=False,
                      title='Actions Taken by Cities to Adapt',
                      titlefont=dict(size=18),
                      width=700, height=400,
                      font=dict(size=10), yaxis_title_text=None)

    vizJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return vizJSON

def create_adaptfactorsplot(respdata):
    """ Creates bar chart showing factors affecting city adaptation to climate hazards.
    Args:
        respdata (Dataframe): data with responses from cities to CDP questionaire.
    Return:
        vizJSON : bar chart plot reduced to  json to be plotted in web UI
    """

    # factors affecting adaption
    adaff = filtq(respdata, '2.2', [1, 2, 3], [1])
    pivind = pd.MultiIndex.from_tuples(list(zip(adaff['Account Number'], adaff['Row Number'])),
                                       names=['Account Number', 'Row Number'])
    adaff['Pivot Index'] = pivind
    adaff = adaff.pivot(values='Response Answer', columns='Column Name', index='Pivot Index')

    adaff = adaff.reset_index() \
        .groupby(['Factors that affect ability to adapt', 'Support / Challenge']) \
        .count() \
        .reset_index()[['Factors that affect ability to adapt', 'Pivot Index', 'Support / Challenge']]
    adaff['Factors that affect ability to adapt'] = adaff['Factors that affect ability to adapt'].apply(
        lambda x: x[0:70])

    adaff = adaff.pivot(index='Factors that affect ability to adapt', values='Pivot Index',
                        columns='Support / Challenge') \
        .fillna(0)
    adaff = adaff[['Support', 'Challenge']]
    adaff = adaff.sort_values(by='Challenge')
    adaff = adaff.reset_index()

    # melting to match plotly input format
    tempdf3 = pd.melt(adaff.tail(15), id_vars='Factors that affect ability to adapt', value_vars=adaff.columns[1:])

    # creating figure
    fig = px.bar(tempdf3, x='value',
                 y='Factors that affect ability to adapt',
                 color='Support / Challenge',
                 barmode='group')

    fig.update_layout(title='Factors Affecting Ability to Adapt',
                      titlefont=dict(size=18),
                      legend_title_text='Listed As',
                      xaxis_title_text='Number of Cities',
                      yaxis_title_text=None)

    vizJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return vizJSON


