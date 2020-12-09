import pandas as pd
import plotly
import plotly.graph_objects as go
import json


def create_sankey(respdata):

    """ Creates a sankey plot matching top climate hazards to demographics.
    Args:
        respdata (Dataframe): response data from CDP questionaire

    Returns:
        vizJSON (json object): sankey plot reduced to json format to be passed onto web app ui.
    """

    ## getting top most listed hazards
    # filtering hazards and probability of hazards
    tempdf2 = respdata[
        (respdata['Question Number'] == '2.1') & ((respdata['Column Number'] == 1) | (respdata['Column Number'] == 3))]
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
                      font_size=10)
    vizJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return vizJSON