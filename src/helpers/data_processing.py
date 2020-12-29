
import pandas as pd

''' Functions to transform data to facilitate clustering.'''

def filtq(qdf, qnum, cnum, rnum):
    '''filters CDP questionaire dataset by question, column and row number'''
    filcon = (qdf['Question Number'].apply(lambda x: x in qnum)) & (qdf['Column Number'].apply(lambda x: x in cnum)) & (qdf['Row Number'].apply(lambda x: x in rnum))
    return qdf[filcon]

def compile_at_city(respdata):
    ''' Compiles response data with rows being questions and response to rows corresponding to cities.'''
    # compile data at city level
    # emissions, emission reduction, energy, oppurtunity, buildings, transport, waste

    resp19 = respdata
    # getting city population and area
    filtdf = filtq(resp19, ['0.5', '0.6'], [1, 3], [1])
    citycompile = filtdf.pivot(values='Response Answer', columns='Column Name', index='Account Number')
    citycompile = citycompile.rename(
        columns={"Land area of the city boundary as defined in question 0.1 (in square km)": "Land Area (sq km)"})
    citycompile = citycompile.apply(pd.to_numeric)

    # getting climate if vulnerability report made
    filtdf = filtq(resp19, ['2.0'], [0], [0])
    pivdf = filtdf.pivot(values='Response Answer', columns='Row Name', index='Account Number')
    pivdf.columns = ['Risk Vulnerability Assessment']
    citycompile = citycompile.join(pivdf, how='outer')

    # getting emissions, CO2 metric tonnes from different scopes
    filtdf = filtq(resp19, ['4.6b'], [1], range(100))
    pivdf = filtdf.pivot(values='Response Answer', columns='Row Name', index='Account Number')
    pivdf = pivdf.apply(pd.to_numeric)
    citycompile = citycompile.join(pivdf, how='outer')

    # getting emiision reduction targets, %target and % achievedd
    filtdf = filtq(resp19, ['5.0a'], [1, 7, 10], range(100))
    filtdf['pivind'] = index = pd.MultiIndex.from_frame(filtdf[['Account Number', 'Row Number']])
    pivdf = filtdf.pivot(values='Response Answer', columns='Column Name', index='pivind')
    pivdf = pivdf[pivdf.Sector == 'All emissions sources included in city inventory']
    pivdf = pivdf.reset_index()
    pivdf['Account Number'] = pivdf.pivind.apply(lambda x: x[0])
    pivdf = pivdf.set_index('Account Number')[['Percentage of target achieved so far', 'Percentage reduction target']]
    pivdf.columns = ['Emission Reduction Achieved (%)', 'Emission Reduction Target (%)']
    pivdf = pivdf.apply(pd.to_numeric)
    citycompile = citycompile.join(pivdf, how='outer')

    # getting energy data, renewable target exists and percentage of different sources
    filtdf = filtq(resp19, ['8.0'], [0], [0])
    pivdf = filtdf.pivot(values='Response Answer', columns='Column Name', index='Account Number')
    pivdf.columns = ['Renewable Target Exists']
    citycompile = citycompile.join(pivdf, how='outer')

    filtdf = filtq(resp19, ['8.0a'], [5], range(20))
    filtdf['Response Answer'] = pd.to_numeric(filtdf['Response Answer'])
    filtdf = filtdf.groupby(['Account Number', 'Column Name']).max()['Response Answer']
    filtdf = filtdf.reset_index(level='Column Name', drop=True).fillna(0)
    citycompile = citycompile.join(filtdf, how='outer')
    citycompile = citycompile.rename(columns={'Response Answer': 'Renewable Energy (%)'})

    # getting oppurtinity data, ESG in investing, business collab, established funds,
    # green growth strategy, development bank funding, green jobs
    filtdf = filtq(resp19, ['6.1', '6.3', '6.4', '6.6', '6.9', '6.11'], [0], [0])
    pivdf = filtdf.pivot(values='Response Answer', columns='Question Name', index='Account Number')
    pivdf = pivdf.rename(
        columns={'How many people within your City are employed in green jobs/ industries?': 'Green Jobs'})
    pivdf['Green Jobs'] = pd.to_numeric(pivdf['Green Jobs'])
    citycompile = citycompile.join(pivdf, how='outer')

    # getting buildings data, CO2 from different buildings
    filtdf = filtq(resp19, ['9.0'], [1], range(10))
    pivdf = filtdf.pivot(values='Response Answer', columns='Row Name', index='Account Number')
    pivdf = pivdf.rename(columns={'Municipal': 'Municipal Buildings',
                                  'Commercial': 'Commerical Buildings',
                                  'Residential': 'Residential Buildings'})
    pivdf.columns = [colname + ' (CO2 Tonnes per capita)' for colname in pivdf.columns]
    pivdf = pivdf.apply(pd.to_numeric)
    citycompile = citycompile.join(pivdf, how='outer')

    # getting transportation data, % of different transport modes
    filtdf = filtq(resp19, ['10.1'], range(10), range(10))
    pivdf = filtdf.pivot(values='Response Answer', columns='Column Name', index='Account Number').fillna(0)
    pivdf = pivdf.apply(pd.to_numeric)
    citycompile = citycompile.join(pivdf, how='outer')

    # getting waste data, waste per capita
    filtdf = filtq(resp19, ['13.0'], [1], [2])
    pivdf = filtdf.pivot(values='Response Answer', columns='Row Name', index='Account Number')
    pivdf = pivdf.apply(pd.to_numeric)
    pivdf2 = pivdf
    citycompile = citycompile.join(pivdf, how='outer')

    # copy before imputing
    unimpcitycomp = citycompile.copy()

    return unimpcitycomp

def impute_data(citycompile):
    ''' Imputes missing data with 0's, mean's or 'No' depending on the feature.'''

    # imputing categorical column NA values with no
    citycompile.loc[:, citycompile.dtypes == 'object'] = citycompile.loc[:, citycompile.dtypes == 'object'].fillna(
        'No').replace('Do not know', 'No')

    # imputing base population with mean
    citycompile['Current population'] = citycompile['Current population'].fillna(
        citycompile['Current population'].mean())

    # dividing emission data and green jobscolumns with base year population
    stdcolumns = ['Agriculture, Forestry and Land Use – Scope 1 (V)',
                  'Industrial Processes and Product Use – Scope 1 (IV)',
                  'Stationary Energy: energy generation supplied to the grid – Scope 1 (I.4.4)',
                  'Stationary Energy: energy use – Scope 1 (I.X.1)',
                  'Stationary Energy: energy use – Scope 2 (I.X.2)',
                  'Stationary Energy: energy use – Scope 3 (I.X.3)',
                  'TOTAL BASIC emissions', 'TOTAL BASIC+ emissions',
                  'TOTAL Scope 1 (Territorial) emissions', 'TOTAL Scope 2 emissions',
                  'TOTAL Scope 3 emissions', 'Transportation – Scope 1 (II.X.1)',
                  'Transportation – Scope 2 (II.X.2)',
                  'Transportation – Scope 3 (II.X.3)',
                  'Waste: waste generated outside the city boundary – Scope 1 (III.X.3)',
                  'Waste: waste generated within the city boundary – Scope 1 (III.X.1)',
                  'Waste: waste generated within the city boundary – Scope 3 (III.X.2)',
                  'Green Jobs']

    citycompile[stdcolumns] = citycompile[stdcolumns].div(citycompile['Current population'], axis=0)

    citycompile.drop(columns=['Current population', 'Land Area (sq km)', 'Projected population'], inplace=True)

    # imputing emission columns with mean
    impmncols = ['Agriculture, Forestry and Land Use – Scope 1 (V)',
                 'Industrial Processes and Product Use – Scope 1 (IV)',
                 'Stationary Energy: energy generation supplied to the grid – Scope 1 (I.4.4)',
                 'Stationary Energy: energy use – Scope 1 (I.X.1)',
                 'Stationary Energy: energy use – Scope 2 (I.X.2)',
                 'Stationary Energy: energy use – Scope 3 (I.X.3)',
                 'TOTAL BASIC emissions', 'TOTAL BASIC+ emissions',
                 'TOTAL Scope 1 (Territorial) emissions', 'TOTAL Scope 2 emissions',
                 'TOTAL Scope 3 emissions', 'Transportation – Scope 1 (II.X.1)',
                 'Transportation – Scope 2 (II.X.2)',
                 'Transportation – Scope 3 (II.X.3)',
                 'Waste: waste generated outside the city boundary – Scope 1 (III.X.3)',
                 'Waste: waste generated within the city boundary – Scope 1 (III.X.1)',
                 'Waste: waste generated within the city boundary – Scope 3 (III.X.2)',
                 'Emission Reduction Target (%)',
                 'All building types (CO2 Tonnes per capita)',
                 'Commerical Buildings (CO2 Tonnes per capita)',
                 'Municipal Buildings (CO2 Tonnes per capita)',
                 'Residential Buildings (CO2 Tonnes per capita)',
                 'Buses (including BRT)',
                 'Cycling',
                 'Ferries/ River boats',
                 'Other',
                 'Private motorized transport',
                 'Rail/Metro/Tram',
                 'Taxis or For Hire Vehicles',
                 'Walking',
                 'Waste generation per capita (kg/person/year)'
                 ]

    citycompile[impmncols] = citycompile[impmncols].fillna(citycompile[impmncols].mean())

    # imputing 0 for na values
    imp0cols = ['Green Jobs',
                'New buildings (CO2 Tonnes per capita)',
                'Emission Reduction Achieved (%)',
                'Renewable Energy (%)'
                ]
    citycompile[imp0cols] = citycompile[imp0cols].fillna(0)

    return citycompile