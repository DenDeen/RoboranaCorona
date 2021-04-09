import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import time
from datetime import date

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
filtered_results.columns = ["date","Sum of first vaccinations"]
filtered_results = filtered_results.groupby(pd.Grouper(key='date', freq='W'), as_index=True).sum()
chart_weekly_total = st.bar_chart(filtered_results)

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

filtered_results = results[["date", "first_dose"]]
filtered_results = filtered_results.groupby(pd.Grouper(key='date', freq='W'), as_index=True).sum()
st.write(len(filtered_results))


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
  p_date = str(slider) + "% will be vaccinated by: " + slider_results.iloc[-1]["date"].strftime('%d/%m/%Y')
  st.write(p_date)

with left_column:
  chart_weekly_total_1 = alt.Chart(filtered_results).mark_line().encode(
    x=alt.X('date:T', axis=alt.Axis(title='')),
    y=alt.Y('percentage:Q', axis=alt.Axis(format='%', title=''))
  )

  chart_weekly_total_2 = alt.Chart(slider_results).mark_area().encode(
    x='date:T',
    y=alt.Y('percentage:Q', axis=alt.Axis(format='%'))
  )

  st.altair_chart(chart_weekly_total_1 + chart_weekly_total_2, use_container_width=True)


st.subheader("""
How many days left?
""")

f_date = date(2020, 12, 28)
n_date = date.today()
l_date = date(2021, 9, 28)
delta_now = l_date - n_date
delta_begin = l_date - f_date

my_bar = st.progress(delta_now.days / delta_begin.days)
st.write("There are " + str(delta_now.days) + " days left till 70% of the population is vaccinated.")


#TODO Push out to web
#TODO Play progress grafieken
#TODO Progress bar
#TODO lijn met prediction date
