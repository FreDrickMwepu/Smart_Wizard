import streamlit as st
from PIL import Image
import pandas as pd
import random
import time
import plotly.express as px
import numpy as np
from streamlit_echarts import st_echarts

# Load the image
image = Image.open('resources/cover.png')

# Sample data generation (to be replaced with actual IoT data fetching)
def get_sample_data():
    bins = ['Bin 1', 'Bin 2', 'Bin 3']
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
def render_gauge(level, bin_id):
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
# Display the image
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

image_bin_levels = Image.open('resources/trashlevels.png')

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

# Display gauges for each bin
st.subheader('Bin Fill Level Gauges')
for idx, row in data.iterrows():
    st.write(f"### {row['Bin ID']}")
    render_gauge(row['Fill Level (%)'], row['Bin ID'])

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
