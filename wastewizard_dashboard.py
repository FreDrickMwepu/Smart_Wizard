import streamlit as st
from PIL import Image
import pandas as pd
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import io

# Load the image
image = Image.open('Resources/Frame 53.png')

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

# Function to create fill level visual
def create_fill_level_visual(levels):
    fig, ax = plt.subplots(figsize=(10, 3))

    bins = ['Empty', 'Low', 'Moderate', 'Mid-level', 'Nearly Full', 'Full']
    colors = ['green', 'lime', 'yellowgreen', 'yellow', 'orange', 'red']

    for i, level in enumerate(levels):
        bin_level = int(level / 20)
        color = colors[bin_level]
        ax.barh(i, level, color=color)
        ax.text(level + 5, i, f'{level}%', va='center', ha='left')

    ax.set_xlim(0, 100)
    ax.set_yticks(np.arange(len(levels)))
    ax.set_yticklabels([f'Bin {i+1}' for i in range(len(levels))])
    ax.set_xlabel('Fill Level (%)')
    ax.set_title('Trash Bin Fill Levels')
    ax.invert_yaxis()

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

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

# Display metrics
st.subheader('Key Metrics')
col1, col2, col3 = st.columns(3)

col1.metric("Average Fill Level (%)", f"{data['Fill Level (%)'].mean():.2f}")
col2.metric("Average Temperature (°C)", f"{data['Temperature (°C)'].mean():.2f}")
col3.metric("Average Humidity (%)", f"{data['Humidity (%)'].mean():.2f}")

# Plot fill levels
st.subheader('Fill Levels Visualization')
fill_levels = data['Fill Level (%)'].tolist()
img_buf = create_fill_level_visual(fill_levels)
st.image(img_buf, use_column_width=True)

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
        img_buf = create_fill_level_visual(fill_levels)
        st.image(img_buf, use_column_width=True)
        st.success("Data updated!")

# Footer
st.markdown("""
**Note:** This is a demonstration dashboard with sample data. In a real-world application, this dashboard would be connected to the WasteWizard smart bins via an IoT communication network.
""")
