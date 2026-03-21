import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import streamlit.components.v1 as components

# 1. PAGE CONFIG
st.set_page_config(page_title="EcoJourney 1M1B Pro", page_icon="🌱", layout="wide")

# 2. THE ULTIMATE CSS OVERRIDE (Targets every layer)
st.markdown("""
    <style>
    /* 1. Remove Top Black Header & Global Background */
    header[data-testid="stHeader"], .stApp {
        background-color: #F8FBF9 !important;
    }
    
    /* 2. Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #81C784 !important;
    }

    /* 3. THE FIX: Force ALL input-related containers to be White */
    /* This targets text inputs, selectboxes, number inputs, and the dropdown lists */
    div[data-baseweb="input"], 
    div[data-baseweb="select"] > div, 
    div[data-testid="stNumberInput"] > div,
    div[role="combobox"] > div,
    div[data-baseweb="popover"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #81C784 !important;
        border-radius: 8px !important;
    }

    /* 4. Force TEXT inside those boxes to be Dark Green/Black for visibility */
    input, span, div[data-testid="stMarkdownContainer"] p, .stSelectbox div {
        color: #1B5E20 !important;
        -webkit-text-fill-color: #1B5E20 !important; /* Forces color in Chrome */
    }

    /* 5. Fix Number Input Buttons (Plus/Minus) */
    button[data-testid="stNumberInputStepUp"], 
    button[data-testid="stNumberInputStepDown"] {
        background-color: #FFFFFF !important;
        color: #1B5E20 !important;
        border: none !important;
    }

    /* 6. Fix for the Dropdown Menu items themselves */
    ul[role="listbox"] li {
        background-color: #FFFFFF !important;
        color: #1B5E20 !important;
    }

    /* 7. Sidebar Titles & Labels */
    h1, h2, h3, label {
        color: #1B5E20 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: bold !important;
    }

    /* 8. Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-left: 5px solid #1B5E20 !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CORE LOGIC
@st.cache_data
def get_trip_info(city1, city2):
    try:
        geolocator = Nominatim(user_agent="1m1b_final_color_override")
        loc1 = geolocator.geocode(city1)
        loc2 = geolocator.geocode(city2)
        if loc1 and loc2:
            d = round(geodesic((loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude)).km, 2)
            return d, loc1, loc2
    except:
        pass
    return 1147.0, None, None 

# Emission Factors
trans_map = {"Flight": 0.25, "Private Car": 0.18, "Train": 0.03, "Bus": 0.08}
diet_map = {"Vegan": 2.1, "Vegetarian": 2.6, "Meat-Heavy": 7.2}

# 4. SIDEBAR
with st.sidebar:
    st.markdown("## 🎒 Trip Planner")
    origin = st.text_input("From City", "Mumbai")
    destination = st.text_input("To City", "Delhi")
    
    st.markdown("---")
    st.markdown("### 🏨 Stay & Lifestyle")
    days = st.number_input("Nights of Stay", 1, 30, 4)
    diet = st.selectbox("Diet Choice", ["Vegan", "Vegetarian", "Meat-Heavy"])
    
    st.markdown("### 🏙️ Local Commute")
    city_km = st.slider("Daily Local km", 0, 100, 20)
    city_mode = st.selectbox("Transport Mode", ["Bus", "Private Car"])

# 5. CALCULATIONS
dist, l1, l2 = get_trip_info(origin, destination)
base_impact = (days * diet_map[diet]) + (city_km * days * trans_map[city_mode])

f_total = (dist * trans_map["Flight"]) + base_impact
c_total = (dist * trans_map["Private Car"]) + base_impact
t_total = (dist * trans_map["Train"]) + base_impact

# 6. MAIN CONTENT
st.markdown("<h1 style='text-align:center;'>🌍 EcoJourney Dashboard</h1>", unsafe_allow_html=True)

if l1 and l2:
    df_map = pd.DataFrame({'lat': [l1.latitude, l2.latitude], 'lon': [l1.longitude, l2.longitude]})
    st.map(df_map)

st.write("---")

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("✈️ Flight Trip", f"{f_total:.1f} kg CO2")
col2.metric("🚗 Car Trip", f"{c_total:.1f} kg CO2")
col3.metric("🚆 Train Trip", f"{t_total:.1f} kg CO2", delta="-85% vs Flight", delta_color="normal")

# Bar Chart
fig = go.Figure(data=[
    go.Bar(x=['Flight', 'Car', 'Train'], y=[f_total, c_total, t_total], 
           marker_color=['#E17055', '#FDCB6E', '#2ecc71'], 
           text=[f"{f_total:.1f}kg", f"{c_total:.1f}kg", f"{t_total:.1f}kg"], textposition='auto')
])
fig.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#2D3436"))
st.plotly_chart(fig, use_container_width=True)

# Recommendation Box
st.markdown("### 💡 1M1B Expert Recommendation")
savings = f_total - t_total
st.success(f"Impact Report: By choosing the **Train** and a **{diet}** diet, you reduce your footprint by **{savings:.1f} kg** of CO2. That is equivalent to planting **{round(savings/21, 1)} trees**!")

# Save Button
st.markdown("---")
components.html(f'''
<button onclick="window.print()" style="background-color:#1B5E20; color:white; padding:12px 24px; border:none; border-radius:8px; width:100%; cursor:pointer; font-weight:bold; font-size:16px;">
    📥 SAVE TRIP REPORT AS PDF
</button>
''', height=60)