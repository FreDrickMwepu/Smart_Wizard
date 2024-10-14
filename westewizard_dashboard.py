import os
import streamlit as st
from PIL import Image
import pandas as pd
import random
import time
import plotly.express as px
import numpy as np
import folium
from streamlit_echarts import st_echarts
from streamlit_folium import folium_static as st_folium
from folium.plugins import AntPath

# Inject Bootstrap CSS
st.markdown("""
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# Inject Tailwind CSS
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# Custom CSS to center the labels and style the scorecards
st.markdown("""
    <style>
    .center-label {
        text-align: center;
    }
    .scorecard {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .scorecard h3 {
        margin: 0;
        font-size: 24px;
        color: #333;
    }
    .scorecard p {
        margin: 5px 0 0;
        font-size: 18px;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Sample data generation (to be replaced with actual IoT data fetching)
def get_sample_data():
    bins = ['Wizard 1', 'Wizard 2', 'Wizard 3']
    data = {
        'Bin ID': bins,
        'Fill Level (%)': [random.randint(0, 100) for _ in bins],
        'Temperature (°C)': [random.uniform(20, 30) for _ in bins],
        'Humidity (%)': [random.uniform(30, 70) for _ in bins],
        'Last Emptied': [pd.Timestamp.now() - pd.Timedelta(hours=random.randint(1, 48)) for _ in bins],
        'latitude': [-15.4167 + random.uniform(-0.01, 0.01) for _ in bins],
        'longitude': [28.2833 + random.uniform(-0.01, 0.01) for _ in bins]
    }
    return pd.DataFrame(data)

# Plotly fill level visualization
def create_fill_level_visual(levels):
    fig = px.bar(x=[f'Bin {i+1}' for i in range(len(levels))], 
                 y=levels, 
                 color=levels, 
                 labels={'x': 'Bins', 'y': 'Fill Level (%)'},
                 title="Trash Bin Fill Levels",
                 color_continuous_scale='RdYlGn_r')
    return fig

# Circular gauge for fill level
def render_gauge(level, bin_id, color='#0cffbb'):
    option = {
        "series": [{
            "type": 'gauge',
            "progress": {"show": "true"},
            "axisLine": {"lineStyle": {"width": 20}},
            "detail": {"formatter": '{value}%'},
            "data": [{"value": level, "name": f"Fill Level - {bin_id}"}]
        }]
    }
    st_echarts(option)

# Streamlit application layout
st.title('WasteWizard Remote Monitoring Dashboard')

# Sample data for vehicle routes and bin locations
vehicle_routes = [
    {'lat': -15.4167, 'lon': 28.2833},
    {'lat': -15.4170, 'lon': 28.2840},
    {'lat': -15.4180, 'lon': 28.2850},
    {'lat': -15.4190, 'lon': 28.2860},
]

bin_locations = [
    {'lat': -15.4167, 'lon': 28.2833, 'bin_id': 'Bin 1'},
    {'lat': -15.4175, 'lon': 28.2845, 'bin_id': 'Bin 2'},
    {'lat': -15.4185, 'lon': 28.2855, 'bin_id': 'Bin 3'},
]

# Load and display the image
image = Image.open('resources/cover.png')
st.image(image, caption='Waste Wizard, The Smart Bin', use_column_width=True)

st.header('Real-time Monitoring of Smart Bins')
st.markdown("""
Welcome to the WasteWizard Remote Monitoring Dashboard. This dashboard provides real-time updates on the status of smart bins deployed in various locations. Monitor fill levels, environmental conditions, and more to optimize waste collection and management.
""")

# Fetch data
data = get_sample_data()

# Display data in a table
st.subheader('Smart Bin Status')
st.dataframe(data)

# Display metrics with color thresholds
st.subheader('Key Metrics')
col1, col2, col3 = st.columns(3)

avg_fill = data['Fill Level (%)'].mean()
avg_temp = data['Temperature (°C)'].mean()
avg_humidity = data['Humidity (%)'].mean()

col1.metric("Average Fill Level (%)", f"{avg_fill:.2f}", delta=None)
col2.metric("Average Temperature (°C)", f"{avg_temp:.2f}", delta=None)
col3.metric("Average Humidity (%)", f"{avg_humidity:.2f}", delta=None)

# Plot fill levels
st.subheader('Fill Levels Visualization')
fill_levels = data['Fill Level (%)'].tolist()
fig = create_fill_level_visual(fill_levels)
st.plotly_chart(fig, use_container_width=True)

# Create a folium map
m = folium.Map(location=[-15.4167, 28.2833], zoom_start=15)

# Add bin locations to the map with custom icons
icon_path = os.path.join(os.path.dirname(__file__), 'resources/cover.png')
for bin in bin_locations:
    icon = folium.CustomIcon(icon_path, icon_size=(30, 30))
    folium.Marker(
        location=[bin['lat'], bin['lon']],
        popup=f"Bin ID: {bin['bin_id']}",
        icon=icon
    ).add_to(m)

# Add vehicle route to the map with AntPath
route = [(point['lat'], point['lon']) for point in vehicle_routes]  # Fix typo here
AntPath(route, color='blue', weight=5, opacity=0.8).add_to(m)

# Display the map in Streamlit
st_folium(m, width=700, height=500)

# Display gauges for each bin
st.subheader('Bin Fill Level Gauges')

# Create columns for each bin
columns = st.columns(len(data))

# Iterate through each bin and place the gauge in the corresponding column
for idx, row in data.iterrows():
    with columns[idx]:
        st.markdown(f'<h3 class="center-label">{row["Bin ID"]}</h3>', unsafe_allow_html=True)
        render_gauge(row['Fill Level (%)'], row['Bin ID'], color='#0cffbb')

# Efficiency Scorecards
st.subheader('Efficiency Scorecards')

# Sample KPI data (replace with actual data)
collection_frequency = 5  # times per week
route_optimization = 85  # percentage
waste_reduction = 10  # percentage

# Display KPIs in columns with custom HTML and CSS
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="scorecard">
        <h3>Collection Frequency</h3>
        <p>{collection_frequency} times/week</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="scorecard">
        <h3>Route Optimization</h3>
        <p>{route_optimization}%</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="scorecard">
        <h3>Waste Reduction</h3>
        <p>{waste_reduction}%</p>
    </div>
    """, unsafe_allow_html=True)

# Map visualization
st.subheader('Smart Bin Locations')
try:
    st.map(data[['latitude', 'longitude']])
except KeyError as e:
    st.error(f"Error displaying map: {e}")

# Automatic update simulation
st.subheader('Live Data Updates')
update_button = st.button("Simulate Live Data Update")

if update_button:
    with st.spinner("Fetching new data..."):
        time.sleep(2)  # Simulate delay
        data = get_sample_data()
        st.dataframe(data)
        try:
            st.map(data[['latitude', 'longitude']])
        except KeyError as e:
            st.error(f"Error displaying map: {e}")
        fill_levels = data['Fill Level (%)'].tolist()
        fig = create_fill_level_visual(fill_levels)
        st.plotly_chart(fig, use_container_width=True)
        st.success("Data updated!")

# Footer
st.markdown("""
**Note:** This is a demonstration dashboard with sample data. In a real-world application, this dashboard would be connected to the WasteWizard smart bins via an IoT communication network.
""")