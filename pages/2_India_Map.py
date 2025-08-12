import streamlit as st
import pandas as pd
import pydeck as pdk

from utils.db_connection import run_query  # ✅ Single point for DB access

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================
st.set_page_config(layout="wide", page_title="📍 India Transaction Heatmap")
st.title("📍 India Transaction Heatmap")

# ==================================================
# 2. LOAD DATA FROM DATABASE
# ==================================================
@st.cache_data(ttl=600)
def load_data_from_db():
    """Loads the transaction data from the database using the shared run_query function."""
    try:
        query = "SELECT * FROM map_transaction_hover"  # ✅ Table name only here
        return run_query(query)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

df = load_data_from_db()
if df is None or df.empty:
    st.stop()

# ==================================================
# 3. DATA PREPARATION
# ==================================================
df.dropna(subset=['latitude', 'longitude', 'amount'], inplace=True)

df = df.rename(columns={
    "amount": "transaction_amount_val",
    "transaction_count": "txn_count",
    "year": "Year",
    "quarter": "Quarter"
})

df['transaction_amount_val'] = pd.to_numeric(df['transaction_amount_val'], errors='coerce')
df.dropna(subset=['transaction_amount_val'], inplace=True)

df['txn_count_str'] = df['txn_count'].apply(lambda x: f"{x:,}")
df['amount_str'] = df['transaction_amount_val'].apply(lambda x: f"₹{x:,.2f}")

# ==================================================
# 4. SIDEBAR FILTERS
# ==================================================
st.sidebar.header("🔎 Filter Map Data")

state_options = sorted(df['state_name'].unique())
selected_states = st.sidebar.multiselect("State(s)", options=state_options, default=state_options)

year_options = sorted(df['Year'].unique())
selected_years = st.sidebar.multiselect("Year(s)", options=year_options, default=year_options)

quarter_options = sorted(df['Quarter'].unique())
selected_quarters = st.sidebar.multiselect("Quarter(s)", options=quarter_options, default=quarter_options)

# ==================================================
# 5. APPLY FILTERS
# ==================================================
filtered_df = df[
    (df['state_name'].isin(selected_states)) &
    (df['Year'].isin(selected_years)) &
    (df['Quarter'].isin(selected_quarters))
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ==================================================
# 6. MAP VISUALIZATION
# ==================================================
min_amt = filtered_df['transaction_amount_val'].min()
max_amt = filtered_df['transaction_amount_val'].max()
max_elevation = 100000

if max_amt > 0:
    filtered_df['elevation'] = (filtered_df['transaction_amount_val'] / max_amt) * max_elevation
else:
    filtered_df['elevation'] = 0

def get_color(amount, min_val, max_val):
    if (max_val - min_val) == 0:
        return [0, 0, 255, 160]
    norm_amt = (amount - min_val) / (max_val - min_val)
    red = int(255 * norm_amt)
    blue = int(255 * (1 - norm_amt))
    return [red, 50, blue, 160]

filtered_df['color'] = filtered_df['transaction_amount_val'].apply(lambda x: get_color(x, min_amt, max_amt))

column_layer = pdk.Layer(
    "ColumnLayer",
    data=filtered_df,
    get_position='[longitude, latitude]',
    get_elevation='elevation',
    get_fill_color='color',
    radius=8000,
    elevation_scale=1,
    pickable=True,
    auto_highlight=True,
    extruded=True,
)

view_state = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.5, pitch=50, bearing=0)

tooltip = {
    "html": """
        <b>State:</b> {state_name}<br/>
        <b>District:</b> {district_name}<br/>
        <b>Transactions:</b> {txn_count_str}<br/>
        <b>Amount:</b> {amount_str}
    """,
    "style": {"backgroundColor": "rgba(0,0,0,0.8)", "color": "white"}
}

st.pydeck_chart(pdk.Deck(
    layers=[column_layer],
    initial_view_state=view_state,
    tooltip=tooltip,
))

st.info("💡 Map shows transaction data by district. Low transaction amounts are in **blue**, and high amounts are in **red**.")
