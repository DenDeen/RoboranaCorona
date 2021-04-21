import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import time
from datetime import date, datetime


results = pd.read_csv('corona_dataset_eu_result.csv')
results['date'] = pd.to_datetime(results['date'])

st.header("Corona Vaccination Progress Prediction")
st.header(" ")

selectbox = st.sidebar.selectbox(
    'What country would you like to see the data of?',
    np.sort(results.country.unique())
)

results_country = results[results['country'] == selectbox]

left_column, right_column = st.beta_columns(2)

with right_column:
  filtered_results = results_country[["date", "percentage"]]
  filtered_results = filtered_results[filtered_results['percentage'] <= 1]

  slider = st.slider(
      '',
      1, 100, (70)
  )

  @st.cache  # 👈 Added this
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


st.header("Acceleration change per week")
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


st.header("Percentage vaccinated per country")
date = st.date_input('Choose date')

all_results = results[["date", "country", "percentage"]]
all_results = results[results['date']<date].groupby('country').tail(1)

mark_bar = alt.Chart(all_results).mark_bar(
  cornerRadiusTopLeft=3,
  cornerRadiusTopRight=3
).encode(
  x=alt.X('country:N', axis=alt.Axis(title='')),
  y=alt.Y('percentage:Q', axis=alt.Axis(format='%', title='')),
  color='country:N'
)

st.altair_chart(mark_bar, use_container_width=True)


st.header("Data")
all_results


st.write("By Mikkel Skovdal")

#TODO grafiek waar je kan aanduiden welke landen je wilt nakijken
#TODO Sexes vergelijken
#TODO Push to web
#TODO Grafieken maken
#TODO procentuele vaccinatie versnelling
