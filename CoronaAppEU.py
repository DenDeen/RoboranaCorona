import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import time
import json
from datetime import date, datetime, timedelta

# 0. INITIALISATION
url = 'https://raw.githubusercontent.com/DenDeen/RoboranaCoronaEU/main/json/europe.json'
source = alt.topo_feature(url, 'continent_Europe_subunits')

results = pd.read_csv('corona_dataset_eu_result.csv')
results['date'] = pd.to_datetime(results['date'])
results = results.replace(to_replace=r'Netherlands', value='the Netherlands', regex=True)

st.title("Corona Vaccination Progress Prediction")
st.write("By Mikkel Skovdal")

selectbox = st.sidebar.selectbox(
    'What region would you like to see the data of?',
    np.sort(results.country.unique())
)
results_country = results[results['country'] == selectbox]

# 1. THE MAP
# SLIDER CREATION
st.header("1. Vaccination progress per country")
st.write("")
initial_value = 1
date_selected = st.empty()
value = date_selected.slider("Select week:", 1, 52, initial_value, 1, key="initial")

current_date = date(2021, 1, 1) + timedelta(days=7*(value-1))

# STATUS CREATION
def get_percentage():
  temp_results = results[results['date'].dt.date<current_date].groupby('country').tail(1)
  temp_results = temp_results[temp_results.country == selectbox]
  temp_results.loc[temp_results['percentage'] > 1, 'percentage'] = 1
  temp_results['percentage'] = pd.Series([round(val, 4) for val in temp_results['percentage']], index = temp_results.index)
  temp_results['percentage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in temp_results['percentage']], index = temp_results.index)
  temp_results = temp_results["percentage"]
  try:
    return str(temp_results.iloc[0])
  except:
    return "0.00%"

date_text = st.empty()
date_text.write("Visualized date: " + str(current_date))
percentage_text = st.empty()
percentage_text.write("Percentage vaccinated in " + selectbox + ": " + get_percentage())

# MAP CREATION
def plot_chart(): 
  variable_list = ['percentage']
  temp_results = results[results['date'].dt.date<current_date].groupby('country').tail(1)
  temp_results.loc[temp_results['percentage'] > 1, 'percentage'] = 1
  temp_results = temp_results[["country", "percentage"]]

  return alt.Chart(source).mark_geoshape(stroke='white',strokeWidth=1
    ).encode(
      color = alt.Color("percentage:Q", 
      legend=alt.Legend(format=".0%"), 
      scale=alt.Scale(domain=[0, 1], scheme="greens")), 
      tooltip=[alt.Tooltip('properties.geounit:N', title='region'), alt.Tooltip('percentage:Q', format='.2%')]
    ).transform_lookup(
      lookup='properties.geounit',
      from_=alt.LookupData(temp_results, 'country', variable_list)
    ).properties(
      width=700,
      height=560
    )
chart = st.empty()
chart.altair_chart(plot_chart())

# MAP ANIMATION
if st.button('Let the fun begin!'):
  for i in range(52):
      current_date = date(2021, 1, 1) + timedelta(days=7*i)
      date_text.write("Visualized date: " + str(current_date))
      percentage_text.write("Percentage vaccinated in " + selectbox + ": " + get_percentage())
      value = date_selected.slider("Select which week", 1, 52, i+1, 1, key="animated")
      chart.altair_chart(plot_chart())
      # Pretend we're doing some computation that takes time.
      time.sleep(0.15)
  st.balloons()

# 2. THE COUNTRY SLIDER
st.header("2. Vaccination progress of " + selectbox)
st.write("")
# COLUMN CREATION
left_column, right_column = st.beta_columns(2)

with right_column:
  filtered_results = results_country[["date", "percentage"]]
  filtered_results = filtered_results[filtered_results['percentage'] <= 1]
  slider = st.slider(
      '',
      1, 100, (70)
  )

  @st.cache()
  def get_date(slider):
    return filtered_results[filtered_results['percentage'] <= (slider/100)], filtered_results[filtered_results['percentage'] <= (slider/100)].iloc[-1]["date"]
  
  slider_results, p_date = get_date(slider)

  st.write(str(slider) + "% will be vaccinated by: " + p_date.strftime('%d/%m/%Y'))

  p_date = date(
    year=p_date.year, 
    month=p_date.month,
    day=p_date.day,
  )
  n_date = date.today()
  f_date = date(2020, 12, 28)
  delta_now = p_date - n_date
  delta_begin = p_date - f_date

  st.write("There are " + str(delta_now.days) + " days left.")

with left_column:

  chart_weekly_total_1 = alt.Chart(filtered_results).mark_line(color="darkgreen").encode(
    x=alt.X('date:T', axis=alt.Axis(title='')),
    y=alt.Y('percentage:Q', axis=alt.Axis(format='%', title=''))
  )

  chart_weekly_total_2 = alt.Chart(slider_results).mark_area(
    line={'color':'darkgreen'},
    color=alt.Gradient(
      gradient='linear',
      stops=[alt.GradientStop(color='#7eb92f', offset=1),
             alt.GradientStop(color='#397648', offset=0)],
      x1=1,
      x2=0,
      y1=1,
      y2=1
      )
  ).encode(
    x='date:T',
    y=alt.Y('percentage:Q', axis=alt.Axis(format='%'))
  )

  st.altair_chart(chart_weekly_total_1 + chart_weekly_total_2, use_container_width=True)

# 3. THE VACCINATION RACE
st.header("3. The vaccination race")
st.write("")
st.write("The current winners:")

@st.cache()
def calculate_current_winners():
  temp_results_winners = results[results['date'].dt.date<date.today()].groupby('country').tail(1).sort_values(by='percentage', ascending=False)
  temp_results_winners.loc[temp_results_winners['percentage'] > 1, 'percentage'] = 1
  temp_results_winners['percentage'] = pd.Series([round(val, 4) for val in temp_results_winners['percentage']], index = temp_results_winners.index)
  temp_results_winners['percentage vaccinated'] = pd.Series(["{0:.2f}%".format(val * 100) for val in temp_results_winners['percentage']], index = temp_results_winners.index)
  temp_results_winners = temp_results_winners[["country", "percentage vaccinated"]]
  temp_results_winners = temp_results_winners.drop(temp_results_winners[(temp_results_winners.country == 'Northern Ireland') | (temp_results_winners.country == 'Wales') | (temp_results_winners.country == 'Scotland') | (temp_results_winners.country == 'England')].index)
  temp_results_winners = temp_results_winners.head(3)
  temp_results_winners.index = np.arange(1, len(temp_results_winners) + 1)
  return temp_results_winners

winners = calculate_current_winners()
winners

st.write("The predicted winners:")

@st.cache(allow_output_mutation=True)
def calculate_future_winners(current_date):
  temp_results_predicted = results[results['date'].dt.date<current_date].groupby('country').tail(1).sort_values(by='percentage', ascending=False)
  temp_results_predicted = temp_results_predicted[temp_results_predicted.percentage >= 1]
  temp_results_predicted = temp_results_predicted.drop(temp_results_predicted[(temp_results_predicted.country == 'Northern Ireland') | (temp_results_predicted.country == 'Wales') | (temp_results_predicted.country == 'Scotland') | (temp_results_predicted.country == 'England')].index)
  temp_results_predicted = temp_results_predicted[["country"]]
  return temp_results_predicted

future_winners = winners.iloc[0:0]
current_date = date.today()
while(len(future_winners)<3):
  current_date += timedelta(days=1)
  future_winners = calculate_future_winners(current_date)

future_winners.index = np.arange(1, len(future_winners) + 1)
future_winners

# 4. PERCENTAGE VACCINATED PER COUNTRY
st.header("4. Percentage vaccinated per country")
st.write("")
date_input = st.date_input('Choose date')

all_results = results[["date", "country", "percentage"]]
all_results = results[results['date'].dt.date<date_input].groupby('country').tail(1)

mark_bar = alt.Chart(all_results).mark_bar(
  cornerRadiusTopLeft=3,
  cornerRadiusTopRight=3
).encode(
  x=alt.X('country:N', axis=alt.Axis(title='')),
  y=alt.Y('percentage:Q', axis=alt.Axis(format='%', title='')),
  color='country:N',
)

st.altair_chart(mark_bar, use_container_width=True)

# 5. ACCELERATION CHANGE PER WEEK
st.header("5. Acceleration change per week")
st.write("")
acceleration_results = results_country[["date", "first_dose", "percentage"]]
acceleration_results = acceleration_results[acceleration_results['percentage'] <= (slider/100)]
acceleration_results = acceleration_results.set_index('date').resample('W').sum()
acceleration_results['difference'] = acceleration_results.drop('percentage', axis=1).diff().fillna(0)
acceleration_results['difference'] = acceleration_results['difference']/acceleration_results['first_dose']
acceleration_results = acceleration_results[:-1].reset_index()
acceleration_chart = alt.Chart(acceleration_results).mark_area(
  line={'color':'darkgreen'},
    color=alt.Gradient(
      gradient='linear',
      stops=[alt.GradientStop(color='#7eb92f', offset=1),
             alt.GradientStop(color='#397648', offset=0)],
      x1=1,
      x2=0,
      y1=1,
      y2=1
      )
).encode(
  x=alt.X('date:T', axis=alt.Axis(title='')),
  y=alt.Y('difference:Q', axis=alt.Axis(format='%', title=''))
)
st.altair_chart(acceleration_chart, use_container_width=True)