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

left_column, right_column = st.beta_columns(2)

with right_column:
  filtered_results = results[["date", "percentage"]]
  filtered_results = filtered_results[filtered_results['percentage'] <= 1]

  slider = st.slider(
      '',
      13, 100, (70)
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





#TODO Push out to web
#TODO Play progress grafieken
#TODO Progress bar
#TODO lijn met prediction date
