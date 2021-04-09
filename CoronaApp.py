import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import time
from datetime import date, datetime


results = pd.read_csv('administered_result.csv')
results['date'] = pd.to_datetime(results['date'])
results['region'] = results['region'].fillna('Varia')
results['percentage'] = results.first_dose.cumsum()/11507163
results['cumulation'] = results.first_dose.cumsum()

st.header("Corona Vaccination Progress Prediction")
st.write("By Mikkel Skovdal")


add_selectbox = st.sidebar.selectbox(
    'What country would you like to see the data of?',
    ('Belgium', 'The Netherlands', 'France', 'Germany', 'All above')
)


st.subheader("""
Predicted amount of vaccinations in Belgium:
""")
filtered_results = results[["date", "first_dose"]]
filtered_results = filtered_results.groupby(pd.Grouper(key='date', freq='W')).sum().reset_index()
chart_weekly_total = alt.Chart(filtered_results).mark_area(
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
  y=alt.Y('first_dose:Q', axis=alt.Axis(title='Total doses per week'))
).interactive()
st.altair_chart(chart_weekly_total, use_container_width=True)


st.subheader("""
Predicted amount of first vaccinations per region in Belgium:
""")
filtered_results = results[["date", "first_dose", "region"]]
filtered_results.columns = ["date","first_dose","Regions"]
chart_weekly_regionally = alt.Chart(filtered_results).mark_line().encode(
  x=alt.X('date:T', axis=alt.Axis(title='')),
  y=alt.Y('first_dose:Q', axis=alt.Axis(title='')),
  color=alt.Color("Regions:N")
).interactive()
st.altair_chart(chart_weekly_regionally, use_container_width=True)


st.subheader("""
Prediction when a certain percentage of belgium is vaccinated:
""")

left_column, right_column = st.beta_columns(2)

with right_column:
  slider = st.slider(
      '',
      13, 100, (70)
  )

  filtered_results = results[["date", "percentage"]]
  filtered_results = filtered_results[filtered_results['percentage'] <= 1]

  slider_results = filtered_results[filtered_results['percentage'] <= (slider/100)]
  p_date = slider_results.iloc[-1]["date"]
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





#TODO Push out to web
#TODO Play progress grafieken
#TODO Progress bar
#TODO lijn met prediction date
