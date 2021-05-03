import altair as alt
import pandas as pd
import requests
import json
import streamlit as st
import time
from datetime import date, datetime, timedelta
from vega_datasets import data

results = pd.read_csv('corona_dataset_eu_result.csv')
results['date'] = pd.to_datetime(results['date'])

# GET TOPOJSON FILE
url = 'https://raw.githubusercontent.com/DenDeen/RoboranaCoronaEU/main/json/europe.json'
source = alt.topo_feature(url, 'continent_Europe_subunits')

# FILTERING DATA BY WEEK SELECTED
initial_value = 18
date_selected = st.slider("Select which week", 1, 52, initial_value, 1, key="initial")
current_date = date(2021, 1, 1) + timedelta(days=7*(date_selected-1))
temp_results = results[results['date'].dt.date<current_date].groupby('country').tail(1)
temp_results.loc[temp_results['percentage'] > 1, 'percentage'] = 1
temp_results = temp_results[["country", "percentage"]]

# CREATE TEXT
status_text = st.write('The chosen week starts on:')
date_text = st.empty()
date_text.write(current_date)

variable_list = ['percentage']

def plot_chart(temp_results):
    return alt.Chart(source).mark_geoshape(
        stroke='white',
        strokeWidth=1
    ).encode(
        color = alt.Color("percentage:Q", scale=alt.Scale(domain=[0, 1], scheme="greens")),
        tooltip=["properties.geounit:N"]
    ).transform_lookup(
        lookup='properties.geounit',
        from_=alt.LookupData(temp_results, 'country', variable_list)
    ).properties(
        width=700,
        height=700
    )

chart = plot_chart(temp_results)
chart

if st.button('Let the fun begin!'):
    for i in range(52):

        current_date = date(2021, 1, 1) + timedelta(days=7*i)
        temp_results = results[results['date'].dt.date<current_date].groupby('country').tail(1)
        temp_results.loc[temp_results['percentage'] > 1, 'percentage'] = 1
        temp_results = temp_results[["country", "percentage"]]
        chart = plot_chart(temp_results)

        # Pretend we're doing some computation that takes time.
        time.sleep(0.1)


    status_text = 'Done!'
    st.balloons()



st.header("Current winner:")

current_date = date(2021, 5, 15)
temp_results = results[results['date'].dt.date<current_date].groupby('country').tail(1)
temp_results.loc[temp_results['percentage'] > 1, 'percentage'] = 1
temp_results = temp_results[["country", "percentage"]]
temp_results = temp_results[temp_results.country != "Wales"]
temp_results = temp_results[temp_results.percentage == temp_results.percentage.max()]
temp_results

st.header("Predicted winner:")

current_date = date(2021, 5, 15)
temp_results = results[results['date'].dt.date<current_date].groupby('country').tail(1)
temp_results.loc[temp_results['percentage'] > 1, 'percentage'] = 1
temp_results = temp_results[["country", "percentage"]]
temp_results = temp_results[temp_results.country != "Wales"]
temp_results = temp_results[temp_results.percentage == temp_results.percentage.max()]
temp_results = temp_results[["country"]]
temp_results