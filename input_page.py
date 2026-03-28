import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math



# --- 0. CALCULATION UTILITY ---
def haversine(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

st.title("🌍 Global Trip Planner")

# --- 1. DATA LOADING (World Cities) ---
@st.cache_data
def load_city_data():
    url = "https://datahub.io/core/world-cities/_r/-/data/world-cities.csv"
    df = pd.read_csv("city_data.csv")
    df['display_name'] = df['name'] + ", " + df['country']
    return df

city_df = load_city_data()
city_list = city_df['display_name'].tolist()

# --- STEP 1: ROUTE SELECTION ---
st.subheader("1. Map Your Journey")
col1, col2 = st.columns(2)

with col1:
    source_name = st.selectbox("From (Source)", options=city_list, 
                               index=city_list.index("Mumbai, India") if "Mumbai, India" in city_list else 0)
with col2:
    dest_name = st.selectbox("To (Destination)", options=city_list, 
                             index=city_list.index("London, United Kingdom") if "London, United Kingdom" in city_list else 1)

src_data = city_df[city_df['display_name'] == source_name].iloc[0]
dest_data = city_df[city_df['display_name'] == dest_name].iloc[0]

# --- THE INTERACTIVE MAP ---
m = folium.Map(location=[(src_data['latitude'] + dest_data['latitude'])/2, 
                         (src_data['longitude'] + dest_data['longitude'])/2], 
               zoom_start=2, tiles="OpenStreetMap")

folium.Marker([src_data['latitude'], src_data['longitude']], 
              popup=f"Source: {source_name}", icon=folium.Icon(color='green', icon='play')).add_to(m)
folium.Marker([dest_data['latitude'], dest_data['longitude']], 
              popup=f"Destination: {dest_name}", icon=folium.Icon(color='red', icon='stop')).add_to(m)

folium.PolyLine([(src_data['latitude'], src_data['longitude']), 
                (dest_data['latitude'], dest_data['longitude'])], 
                color="blue", weight=3, opacity=0.7, dash_array='10, 10').add_to(m)

st_folium(m, width=1100, height=450, key="trip_map")
# --- STEP 2: TRAVEL, STAY & LOCAL COMMUTE ---
st.divider()
st.subheader("2. Travel & Stay Details")

# Define a list of cities known for Public Transport (for logic)
public_transport_hubs = ["London", "Mumbai", "New York", "Paris", "Tokyo", "Berlin", "Singapore"]

# Check if the destination is a major hub
is_hub = any(hub in dest_name for hub in public_transport_hubs)

c1, c2, c3, c4 = st.columns(4)

with c1:
    transport_mode = st.selectbox("Main Transport", ["Flight (Economy)", "Flight (Business)", "Train", "Petrol Car", "EV"])
with c2:
    stay_days = st.number_input("Days", min_value=1, value=1)
with c3:
    hotel_type = st.selectbox("Hotel", ["Standard", "Luxury", "Budget", "Eco-Resort"])

with c4:
    # SMART LOGIC: Change options based on the city
    if is_hub:
        commute_options = ["Public Transport (Metro/Bus)", "Walking/Cycling", "Taxis", "Rental EV"]
    else:
        commute_options = ["Rental Car (Petrol)", "Walking", "Local Taxis"]
        
    local_commute = st.selectbox("Local Commute", options=commute_options)

# --- STEP 3: FINAL CONFIRMATION & NAVIGATION ---
st.divider()

# Center the button using columns
_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    if st.button("Calculate My Carbon Footprint ➔", use_container_width=True):
        # 1. Perform the distance calculation
        dist_km = haversine(src_data['latitude'], src_data['longitude'], 
                            dest_data['latitude'], dest_data['longitude'])
        
        # 2. Save ALL data to session state so the next page can see it
        st.session_state.trip_ready = {
            "source": source_name,
            "dest": dest_name,
            "distance": dist_km * 2,
            "mode": transport_mode,
            "days": stay_days,
            "hotel": hotel_type,
            "local_commute": local_commute
        }
        
        # 3. THE MAGIC LINE: Switch to the analysis page automatically
        st.switch_page("calculation_page.py")
