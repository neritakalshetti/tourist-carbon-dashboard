import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. DATA CHECK & LOADING ---
# This ensures the page doesn't crash if someone refreshes it
if "trip_ready" not in st.session_state:
    st.warning("⚠️ No trip data found! Please go back to the 'Plan Trip' page.")
    if st.button("⬅️ Back to Planner"):
        st.switch_page("input_page.py")
    st.stop()

# Retrieve the data dictionary we saved on the first page
data = st.session_state.trip_ready

# Extract the variables safely from the dictionary
source_name = data['source']
dest_name = data['dest']
dist = data['distance']
mode = data['mode']
days = data['days']
hotel = data['hotel']
local_commute = data['local_commute']

st.title("📊 Your Trip's Carbon Impact")
st.write(f"Showing analysis for: **{source_name}** to **{dest_name}**")

# --- 2. EMISSION FACTORS (kg CO2) ---
transport_factors = {
    "Flight (Economy)": 0.15, "Flight (Business)": 0.40, 
    "Train": 0.04, "Petrol Car": 0.18, "EV": 0.05
}

hotel_factors = {
    "Standard": 15.0, "Luxury": 35.0, "Budget": 10.0, "Eco-Resort": 6.0
}

commute_factors = {
    "Public Transport (Metro/Bus)": 2.0, "Walking/Cycling": 0.0, 
    "Rental Car (Petrol)": 12.0, "Rental EV": 3.0, "Taxis": 8.0, "Local Taxis": 8.0
}

# --- 3. THE MATH ---
t_emissions = dist * transport_factors.get(mode, 0.15)
h_emissions = days * hotel_factors.get(hotel, 15.0)
c_emissions = days * commute_factors.get(local_commute, 2.0)
total_co2 = t_emissions + h_emissions + c_emissions

# --- 4. DISPLAY METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("Total CO2", f"{total_co2:.1f} kg")
col2.metric("Distance", f"{dist:.0f} km")
col3.metric("Daily Local Impact", f"{commute_factors.get(local_commute, 0)} kg")

st.divider()

# --- 5. VISUALIZATION ---
chart_data = pd.DataFrame({
    "Category": ["Travel", "Stay", "Local"],
    "kg CO2": [t_emissions, h_emissions, c_emissions]
})

fig = px.pie(chart_data, values='kg CO2', names='Category', hole=0.4,
             color_discrete_sequence=px.colors.sequential.Greens_r)
st.plotly_chart(fig, use_container_width=True)

# --- 6. NAVIGATION BACK ---
if st.button("⬅️ Plan Another Trip"):
    st.switch_page("input_page.py")