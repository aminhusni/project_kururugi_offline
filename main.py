import datetime
import pytz
import os
import pathlib
import csv
import urllib.request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Get the current generation time in MYT timezone
timeZ_My = pytz.timezone('Asia/Kuala_Lumpur')
now = datetime.datetime.now(timeZ_My)
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

# Get datapoints from official CITF Malaysia and process as CSV with Pandas
url = "https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/vaccination/vax_malaysia.csv"
df = pd.read_csv(url)

last_date_data = df['date'].iloc[-1:].item()

# Get a 7-day rolling dataset to be plotted into the vaccination_rate graph
df['7_rolling_avg'] = df['total_daily'].rolling(7).mean()

# Plot the graph
# Vaccination rate daily
vaccination_rate = px.line(df, x = 'date', y = ['total_daily', '7_rolling_avg'],
                            color_discrete_map={
                                "total_daily": "#1f822c",
                                "7_rolling_avg": "#FF9D3C",
                            },
                            labels={
                                "date": "",
                                "value": "Doses"
                            },
                            title='Daily Vaccination Rate (Doses)')

vaccination_rate.add_trace(go.Indicator(
                                        mode = "number+delta",
                                        value = df['7_rolling_avg'].iloc[-1:].item(),
                                        number = {'prefix': "Avg "},
                                        delta = {
                                            'reference' : df['7_rolling_avg'].iloc[-2].item(),
                                            "valueformat": ",.0f",
                                            'increasing.color': "#FF9D3C",
                                            'decreasing.color': "#FF9D3C",
                                        },
                                        gauge = {
                                            'axis': {'visible': False}
                                        },
                                        domain = {'x': [0.03, 0.35], 'y': [0.60, 0.95]}
))

# Make the line labeling nicer
series_names = ["Daily doses", "Week Roll Avg"]

for idx, name in enumerate(series_names):
    vaccination_rate.data[idx].name = name


# Total vaccination dose (overall)
vaccinated_total = px.line(df, x = 'date', y = 'total_cumul',
                            labels={
                                "date": "",
                                "total_cumul": "Doses to date"
                            },
                            title='Total Vaccination Dose Administered')
vaccinated_total.update_traces(line_color='#1f822c')

vaccinated_total.add_trace(go.Indicator(
                                        mode = "number+delta",
                                        value = df['total_cumul'].iloc[-1:].item(),
                                        delta = {
                                            'reference' : df['total_cumul'].iloc[-2].item(),
                                            "valueformat": ",0f"
                                        },
                                        gauge = {
                                            'axis': {'visible': False}
                                        },
                                        domain = {'x': [0.02, 0.35], 'y': [0.60, 0.95]}
))


# Calculate the amount of people vaccinated vs unvaccinated
# Get 1 dose total to date
single_dose_total = df['dose1_cumul'].iloc[-1:].item()
population_total = 32764602
# Get unvaccinated using maths lol #QuickMaths
unvaccinated = population_total - single_dose_total

# Put the calculations into data frame
progress_frame = [{'type': 'Vaccinated', 'total': single_dose_total},
                {'type': 'Unvaccinated', 'total': unvaccinated} 
                    ]
df2 = pd.DataFrame(progress_frame)

# Pie chart
progress_total = px.pie(df2, title='Vaccination Progress (at least 1 dose)', values='total', names='type', color='type',
                        color_discrete_map={
                            'Vaccinated': '#3cb64c',
                            'Unvaccinated': '#29255f'
                            }
                        )

# Get 2 dose total to date
double_dose_total = df['dose2_cumul'].iloc[-1:].item()
population_total = 32764602
# Get unvaccinated using maths again #QuickMaths
unvaccinated = population_total - double_dose_total

# Put the calculations into data frame
progress2_frame = [{'type': 'Vaccinated', 'total': double_dose_total},
                {'type': 'Unvaccinated', 'total': unvaccinated} 
                    ]
df3 = pd.DataFrame(progress2_frame)

# Pie chart
progress2_total = px.pie(df3, title='Vaccination Progress (2 doses)', values='total', names='type', color='type',
                        color_discrete_map={
                            'Vaccinated': '#3cb64c',
                            'Unvaccinated': '#29255f'
                            }
                        )

# Generate day name based on date
df['date'] = pd.to_datetime(df['date'])
df['day_of_week'] = df['date'].dt.day_name()

# Plot the graph
day_trend = px.bar(df, x='day_of_week', y='total_daily', 
                    category_orders={'day_of_week': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                    labels={
                        "day_of_week": "",
                        "total_daily": "Total doses administered to date"
                    },
                    title='Doses administered by day distribution')
day_trend.update_traces(marker_color='#1f822c')

# PER STATE DATA
# Get datapoints for per state in Malaysia
url = "https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/vaccination/vax_state.csv"
df = pd.read_csv(url)
df_trim = df.iloc[-16:]
df_trim = df_trim.sort_values('total_cumul')

state_progress = px.bar(df_trim, x="total_cumul", y="state", 
                        labels={
                            "total_cumul": "Doses",
                            "state": "States",
                        },
                        title='Doses administed by state',

                        orientation='h')
state_progress.update_traces(marker_color='#1f822c')

# Get per state population for the latest total vaccinated dose to date
df_trim = df.iloc[-16:]
df_trim_dose = df_trim.sort_values('state')
df_trim_dose = df_trim_dose.reset_index()

# Get static population for state
url = "https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/static/population.csv"
df = pd.read_csv(url)
df_trim = df.iloc[1:]
df_trim_pop = df_trim.sort_values('state')
df_trim_pop = df_trim_pop.reset_index()

# Do some not very quick maths to get vaccinated percentage of each state
df_trim_pop['vax1_pct'] = (df_trim_dose['dose1_cumul']/df_trim_pop['pop'])*100
df_trim_pop['vax2_pct'] = (df_trim_dose['dose2_cumul']/df_trim_pop['pop'])*100
df_trim_pop['unvax1'] = ((df_trim_pop['pop']-df_trim_dose['dose1_cumul'])/df_trim_pop['pop'])*100
df_trim_pop['unvax2'] = ((df_trim_pop['pop']-df_trim_dose['dose2_cumul'])/df_trim_pop['pop'])*100

state_dose1_pct = px.bar(df_trim_pop.sort_values('vax1_pct'), x=["vax1_pct", "unvax1"], y="state", 
                        labels={
                            "state": "States",
                            "value": "Percentage"
                        },
                        color_discrete_map={
                            'vax1_pct': '#3cb64c',
                            'unvax1': '#29255f'
                            },
                        title='Percentage vaccinated by state (at least 1 dose)',
                        orientation='h')

# Make the bar labeling nicer
state_dose1_pct.data[0].name = "Vaccinated"
state_dose1_pct.data[1].name = "Population"
state_dose1_pct.data[1].hovertemplate = "Population"


state_dose2_pct = px.bar(df_trim_pop.sort_values('vax2_pct'), x=["vax2_pct", "unvax2"], y="state", 
                        labels={
                            "state": "States",
                            "value": "Percentage"
                        },
                        color_discrete_map={
                            'vax2_pct': '#3cb64c',
                            'unvax2': '#29255f'
                            },
                        title='Percentage vaccinated by state (2 doses)',
                        orientation='h')

# Make the bar labeling nicer
state_dose2_pct.data[0].name = "Vaccinated"
state_dose2_pct.data[1].name = "Population"
state_dose2_pct.data[1].hovertemplate = "Population"

# Bar graph showing each state's progress based on percentage (per 100)

# Convert plotted graph into HTML div
daily_rate_plot = vaccination_rate.to_html(full_html=False, include_plotlyjs=False)
daily_rate_plot2 = vaccinated_total.to_html(full_html=False, include_plotlyjs=False)
progress_plot = progress_total.to_html(full_html=False, include_plotlyjs=False)
progress2_plot = progress2_total.to_html(full_html=False, include_plotlyjs=False)
day_trend_plot = day_trend.to_html(full_html=False, include_plotlyjs=False)
state_plot = state_progress.to_html(full_html=False, include_plotlyjs=False)
state_dose1_plot = state_dose1_pct.to_html(full_html=False, include_plotlyjs=False) 
state_dose2_plot = state_dose2_pct.to_html(full_html=False, include_plotlyjs=False) 

# Crude HTML templates
HeadTemplate = open(pathlib.Path(__file__).parent / 'html_header.html', 'r').read()    
Close = '</div>'
RowOpen = '<div class="row">'
ColOpen = '<div class="col-1">'
FootClose = '</body></html>'

# Generate the static HTML page
with open("index.html", "w") as f:
    f.write(HeadTemplate)
    f.write("<h1>Vaccination Statistics Malaysia</h1>")
    f.write("<a href='https://kururugi.blob.core.windows.net/kururugi/about.html'>Technical details & about</a><br>Coded by: Amin Husni (aminhusni@gmail.com)<br><br>")
    f.write("Data refreshed: " + current_time + " (MYT)<br>")
    f.write("Latest date in data: " + last_date_data + "<br><br></div>")
    f.write(Close)

    f.write(RowOpen)
    f.write(ColOpen)
    f.write(daily_rate_plot)
    f.write(Close)
   
    f.write(ColOpen)
    f.write(daily_rate_plot2)
    f.write(Close)
    f.write(Close)

    f.write(RowOpen)
    f.write(ColOpen)
    f.write(day_trend_plot)
    f.write(Close)
    f.write(ColOpen)
    f.write(state_plot)
    f.write(Close)
    f.write(Close)

    f.write(RowOpen)
    f.write(ColOpen)
    f.write(state_dose1_plot)
    f.write(Close)
    f.write(ColOpen)
    f.write(state_dose2_plot)
    f.write(Close)
    f.write(Close)

    f.write(RowOpen)
    f.write(ColOpen)
    f.write(progress_plot)
    f.write(Close)
    f.write(ColOpen)
    f.write(progress2_plot)
    f.write(Close)
    f.write(Close)

    f.write(RowOpen)
    f.write("<br>Licenses: Official datapoint: <a href='https://www.data.gov.my/p/pekeliling-data-terbuka'>Pekeliling Pelaksanaan Data Terbuka Bil.1/2015 (Appendix B)</a> <br>")
    f.write("<a href='https://github.com/aminhusni/project_kururugi/blob/main/LICENSE'>Copyright (C) 2021 Amin Husni. MIT License</a><a href='https://kururugi.blob.core.windows.net/kururugi/about.html'>    More & Contact</a>")
    f.write(Close)