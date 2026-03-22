import streamlit as st

# Define the pages
page1 = st.Page("input_page.py", title="Plan Trip", icon="📍")
page2 = st.Page("calculation_page.py", title="View Analysis", icon="📊")

# Setup Navigation
pg = st.navigation([page1, page2])
pg.run()