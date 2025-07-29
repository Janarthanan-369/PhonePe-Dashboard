# map in 3D using pydeck

# import streamlit as st
# import pandas as pd
# import pydeck as pdk
# import os

# # === 📄 Load the cleaned hover data ===
# CSV_PATH = "/Users/macbook/Desktop/DS_Project/Phone_pe_pluse/PhonePe_Dashboard/map_transaction_hover.csv"

# st.set_page_config(layout="wide", page_title="📍 India Transaction Overview Map")
# st.title("📍 India Transaction Overview Map")

# # ✅ Step 1: Load and validate the CSV file
# if not os.path.exists(CSV_PATH):
#     st.error("❌ CSV file not found. Please check the file path.")
#     st.stop()

# df = pd.read_csv(CSV_PATH)

# # ✅ Define required columns and check their presence
# required_columns = [
#     "state", "district", "transaction_count",
#     "transaction_amount", "latitude", "longitude"
# ]

# if not all(col in df.columns for col in required_columns):
#     st.error("❌ The CSV file is missing one or more required columns.")
#     st.write("Expected columns:", required_columns)
#     st.write("Available columns:", df.columns.tolist())
#     st.stop()

# # ✅ Rename columns for consistency in tooltip
# df = df.rename(columns={
#     "state": "state_name",
#     "district": "district_name",
#     "transaction_count": "txn_count"
# })

# # ✅ Normalize elevation based on transaction amount (for 3D effect)
# max_elevation = 5000
# df["elevation"] = df["transaction_amount"] / df["transaction_amount"].max() * max_elevation

# # === 🎛️ Sidebar Filters ===
# with st.sidebar:
#     st.header("🔎 Filter Map Data")
#     min_amt = int(df["transaction_amount"].min())
#     max_amt = int(df["transaction_amount"].max())

#     selected_range = st.slider(
#         "Filter by Transaction Amount (₹)",
#         min_value=min_amt,
#         max_value=max_amt,
#         value=(min_amt, max_amt)
#     )

#     df = df[
#         (df["transaction_amount"] >= selected_range[0]) &
#         (df["transaction_amount"] <= selected_range[1])
#     ]

# # ✅ Configure PyDeck Hexagon Layer
# hex_layer = pdk.Layer(
#     "HexagonLayer",
#     data=df,
#     get_position='[longitude, latitude]',
#     get_elevation='elevation',
#     radius=8000,
#     get_fill_color='[138, 43, 226, 160]',
#     pickable=True,
#     auto_highlight=True,
#     extruded=True
# )

# # ✅ Define initial view state
# view_state = pdk.ViewState(
#     latitude=22.5,
#     longitude=78.9,
#     zoom=3.2,
#     pitch=25,
#     bearing=0
# )

# # ✅ Tooltip configuration
# tooltip = {
#     "html": """
#         <b>🗺️ State:</b> {state_name}<br/>
#         <b>🏙️ District:</b> {district_name}<br/>
#         <b>💳 Transactions:</b> {txn_count:,}<br/>
#         <b>💰 Amount:</b> ₹{transaction_amount:,.2f}
#     """,
#     "style": {"color": "white"}
# }

# # ✅ Render the map
# deck = pdk.Deck(
#     layers=[hex_layer],
#     initial_view_state=view_state,
#     tooltip=tooltip,
#     # Optional: Uncomment to use a custom map style
#     # map_style="mapbox://styles/mapbox/light-v10"
# )

# st.pydeck_chart(deck)



# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import os

# # === 📄 Load Data ===
# CSV_PATH = "/Users/macbook/Desktop/DS_Project/Phone_pe_pluse/PhonePe_Dashboard/map_transaction_hover.csv"
# st.set_page_config(layout="wide", page_title="📍 India Transaction Overview Map")
# st.title("📍 India Transaction Overview Map")

# if not os.path.exists(CSV_PATH):
#     st.error("❌ CSV not found")
#     st.stop()
# df = pd.read_csv(CSV_PATH)

# # Rename for consistency
# df = df.rename(columns={
#     "state": "State",
#     "district": "District",
#     "transaction_count": "Txn_Count",
#     "transaction_amount": "Amount",
#     "year": "Year",
#     "quarter": "Quarter"
# })

# # === 🎛️ Sidebar Filters ===
# states = st.sidebar.multiselect("Select State(s):", sorted(df["State"].unique()), default=df["State"].unique())
# years = st.sidebar.multiselect("Select Year(s):", sorted(df["Year"].unique()), default=df["Year"].unique())
# quarters = st.sidebar.multiselect("Select Quarter(s):", sorted(df["Quarter"].unique()), default=df["Quarter"].unique())

# min_amt, max_amt = int(df["Amount"].min()), int(df["Amount"].max())
# amt_slider = st.sidebar.slider("Amount Range:", min_amt, max_amt, (min_amt, max_amt))

# # Apply filters
# df = df[df["State"].isin(states)]
# df = df[df["Year"].isin(years)]
# df = df[df["Quarter"].isin(quarters)]
# df = df[(df["Amount"] >= amt_slider[0]) & (df["Amount"] <= amt_slider[1])]

# if df.empty:
#     st.warning("No data for selected filters")
#     st.stop()

# # === 🔢 Number formatting ===
# def fmt_amt(x):
#     if x >= 1e7:
#         return f"₹{x/1e7:.2f} Cr"
#     elif x >= 1e5:
#         return f"₹{x/1e5:.2f} L"
#     else:
#         return f"₹{x:,.0f}"

# df["Amount_label"] = df["Amount"].apply(fmt_amt)

# # === 📍 Plotly 3D ===
# fig = go.Figure(go.Scatter3d(
#     x=df["longitude"],
#     y=df["latitude"],
#     z=df["Amount"],
#     mode="markers",
#     marker=dict(
#         size=4,
#         color=df["Amount"],
#         colorscale="Viridis",
#         opacity=0.7,
#     ),
#     customdata=df[["State", "District", "Year", "Quarter", "Txn_Count", "Amount_label"]],
#     hovertemplate=(
#         "<b>State:</b> %{customdata[0]}<br>"
#         "<b>District:</b> %{customdata[1]}<br>"
#         "<b>Year:</b> %{customdata[2]} | %{customdata[3]}<br>"
#         "<b>Txn Count:</b> %{customdata[4]:,}<br>"
#         "<b>Amount:</b> %{customdata[5]}<extra></extra>"
#     )
# ))

# fig.update_layout(
#     title="3D Transactions by District",
#     scene=dict(
#         xaxis_title="Longitude",
#         yaxis_title="Latitude",
#         zaxis_title="Transaction Amount (₹)",
#         xaxis=dict(showbackground=False),
#         yaxis=dict(showbackground=False),
#         zaxis=dict(showbackground=False),
#     ),
#     margin=dict(l=0, r=0, t=40, b=0),
#     height=700,
# )

# st.plotly_chart(fig, use_container_width=True)

# # === 📋 Summary Metrics ===
# st.sidebar.markdown("### Top States by Amount")
# top_states = df.groupby("State")["Amount"].sum().sort_values(ascending=False).head(5)
# for stt, val in top_states.items():
#     st.sidebar.write(f"{stt}: {fmt_amt(val)}")

# 2D map

# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import os

# # === 📄 Load Data ===
# CSV_PATH = "/Users/macbook/Desktop/DS_Project/Phone_pe_pluse/PhonePe_Dashboard/map_transaction_hover.csv"
# st.set_page_config(layout="wide", page_title="📍 India Transaction Overview Map")
# st.title("📍 India Transaction Overview Map")

# if not os.path.exists(CSV_PATH):
#     st.error("❌ CSV not found")
#     st.stop()

# df = pd.read_csv(CSV_PATH)

# # Rename columns for consistency
# df = df.rename(columns={
#     "state": "State",
#     "district": "District",
#     "transaction_count": "Txn_Count",
#     "transaction_amount": "Amount",
#     "latitude": "Latitude",
#     "longitude": "Longitude"
# })

# # === 🎛️ Sidebar Filters ===
# states = st.sidebar.multiselect("Select State(s):", sorted(df["State"].unique()), default=df["State"].unique())

# min_amt, max_amt = int(df["Amount"].min()), int(df["Amount"].max())
# amt_slider = st.sidebar.slider("Amount Range:", min_amt, max_amt, (min_amt, max_amt))

# # Apply filters
# df = df[df["State"].isin(states)]
# df = df[(df["Amount"] >= amt_slider[0]) & (df["Amount"] <= amt_slider[1])]

# if df.empty:
#     st.warning("⚠️ No data available for selected filters.")
#     st.stop()

# # === 💱 Format large numbers in Indian style
# def fmt_amt(x):
#     if x >= 1e7:
#         return f"₹{x/1e7:.2f} Cr"
#     elif x >= 1e5:
#         return f"₹{x/1e5:.2f} L"
#     else:
#         return f"₹{x:,.0f}"

# df["Amount_label"] = df["Amount"].apply(fmt_amt)

# # === 📍 3D Plotly Visualization ===
# fig = go.Figure(go.Scatter3d(
#     x=df["Longitude"],
#     y=df["Latitude"],
#     z=df["Amount"],
#     mode="markers",
#     marker=dict(
#         size=4,
#         color=df["Amount"],
#         colorscale="Viridis",
#         opacity=0.7,
#     ),
#     customdata=df[["State", "District", "Txn_Count", "Amount_label"]],
#     hovertemplate=(
#         "<b>State:</b> %{customdata[0]}<br>"
#         "<b>District:</b> %{customdata[1]}<br>"
#         "<b>Txn Count:</b> %{customdata[2]:,}<br>"
#         "<b>Amount:</b> %{customdata[3]}<extra></extra>"
#     )
# ))

# fig.update_layout(
#     title="3D Transactions by District",
#     scene=dict(
#         xaxis_title="Longitude",
#         yaxis_title="Latitude",
#         zaxis_title="Transaction Amount (₹)",
#         xaxis=dict(showbackground=False),
#         yaxis=dict(showbackground=False),
#         zaxis=dict(showbackground=False),
#     ),
#     margin=dict(l=0, r=0, t=40, b=0),
#     height=700,
# )

# st.plotly_chart(fig, use_container_width=True)

# # === 📋 Sidebar Summary Metrics ===
# st.sidebar.markdown("### 🏆 Top States by Total Amount")
# top_states = df.groupby("State")["Amount"].sum().sort_values(ascending=False).head(5)
# for stt, val in top_states.items():
#     st.sidebar.write(f"{stt}: {fmt_amt(val)}")




# main.py (Streamlit App)

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import psycopg2
# from psycopg2 import sql

# # ========================
# # PostgreSQL DB CONNECTION
# # ========================
# def load_data():
#     conn = psycopg2.connect(
#         dbname="postgres",
#         user="postgres",
#         password="1234",
#         host="localhost",
#         port="5432"
#     )

#     query = """
#         SELECT
#             state_name,
#             year,
#             quarter, 
#             district_name,
#             transaction_count,
#             amount
#         FROM map_transaction_hover
#     """
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# # ========================
# # FORMAT INDIAN NUMBERS
# # ========================
# def format_inr(amount):
#     if pd.isnull(amount):
#         return "NA"
#     abs_amt = abs(amount)
#     if abs_amt >= 1e7:
#         return f"₹{amount/1e7:.1f} Cr"
#     elif abs_amt >= 1e5:
#         return f"₹{amount/1e5:.1f} L"
#     elif abs_amt >= 1e3:
#         return f"₹{amount/1e3:.1f} K"
#     else:
#         return f"₹{amount:.0f}"

# # ========================
# # STREAMLIT APP
# # ========================
# def main():
#     st.set_page_config(layout="wide")
#     st.title("📍 PhonePe India Map – Transactions Dashboard")

#     df = load_data()

#     # Filter Sidebar
#     with st.sidebar:
#         st.header("🔍 Filter Options")
#         all_years = sorted(df["year"].unique())
#         all_quarters = sorted(df["quarter"].unique())
#         all_states = sorted(df["state_name"].unique())

#         selected_years = st.multiselect("Select Year(s):", all_years, default=all_years)
#         selected_quarters = st.multiselect("Select Quarter(s):", all_quarters, default=all_quarters)
#         selected_states = st.multiselect("Select State(s):", all_states, default=all_states)

#         view_mode = st.radio("🗺️ Select Map View: ", ["2D View", "3D View"])

#     # Apply filters
#     filtered_df = df[
#         (df["year"].isin(selected_years)) &
#         (df["quarter"].isin(selected_quarters)) &
#         (df["state_name"].isin(selected_states))
#     ]

#     if filtered_df.empty:
#         st.warning("No data found for selected filters.")
#         return

#     # Aggregate data per district for current filter
#     agg_df = filtered_df.groupby(["state_name", "district_name"], as_index=False).agg({
#         "amount": "sum",
#         "transaction_count": "sum"
#     })
#     agg_df["amount_fmt"] = agg_df["amount"].apply(format_inr)

#     # Sample district-level coordinates (must be preloaded in real app)
#     # This must be merged with a geospatial file for real implementation
#     agg_df["lat"] = 20 + (agg_df.index % 10)  # mock data
#     agg_df["lon"] = 77 + (agg_df.index % 10)  # mock data

#     hover_text = (
#         "<b>State:</b> " + agg_df["state_name"] +
#         "<br><b>District:</b> " + agg_df["district_name"] +
#         "<br><b>Amount:</b> " + agg_df["amount_fmt"] +
#         "<br><b>Txn Count:</b> " + agg_df["transaction_count"].astype(str)
#     )

#     # Plot Map
#     if view_mode == "2D View":
#         fig = px.scatter_geo(
#             agg_df,
#             lat="lat",
#             lon="lon",
#             size="amount",
#             hover_name="district_name",
#             hover_data={"lat": False, "lon": False, "amount": False},
#             text=agg_df["amount_fmt"],
#             projection="natural earth",
#             template="plotly_dark"
#         )
#         fig.update_traces(marker=dict(color='lightblue', line=dict(width=1, color='darkblue')),
#                           hovertemplate=hover_text)

#     else:  # 3D View
#         fig = px.scatter_3d(
#             agg_df,
#             x="lon",
#             y="lat",
#             z="amount",
#             color="state_name",
#             size="amount",
#             hover_name="district_name",
#             text=agg_df["amount_fmt"],
#             template="plotly_dark",
#         )
#         fig.update_traces(marker=dict(line=dict(width=0.5, color='black')),
#                           hovertemplate=hover_text)

#     st.plotly_chart(fig, use_container_width=True)

# if __name__ == "__main__":
#     main()


# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import psycopg2

# # === CONFIGURATION ===
# DB_CONFIG = {
#     "dbname": "postgres",
#     "user": "postgres",
#     "password": "1234",
#     "host": "localhost",
#     "port": "5432"
# }

# CSV_PATH = "/Users/macbook/Desktop/DS_Project/Phone_pe_pluse/PhonePe_Dashboard/map_transaction_hover.csv"
# TABLE_NAME = "map_transaction_hover"

# # === HELPER: Format amount in Indian style ===
# def format_indian_currency(amount):
#     crore = 10**7
#     lakh = 10**5
#     if amount >= crore:
#         return f"₹{amount / crore:.2f} Cr"
#     elif amount >= lakh:
#         return f"₹{amount / lakh:.2f} L"
#     elif amount >= 1000:
#         return f"₹{amount / 1000:.2f} K"
#     else:
#         return f"₹{amount:.2f}"

# # === STEP 1: Load CSV with lat/lon ===
# @st.cache_data
# def load_csv_with_latlon():
#     df_csv = pd.read_csv(CSV_PATH)
#     df_csv = df_csv[['state_name', 'district_name', 'latitude', 'longitude']]
#     df_csv['state_name'] = df_csv['state_name'].str.strip().str.lower()
#     df_csv['district_name'] = df_csv['district_name'].str.strip().str.lower()
#     return df_csv

# # === STEP 2: Load filtered data from PostgreSQL ===
# def fetch_postgres_data(state, year, quarter):
#     conn = psycopg2.connect(**DB_CONFIG)
#     query = f"""
#         SELECT state_name, district_name, year, quarter, transaction_count, amount
#         FROM {TABLE_NAME}
#         WHERE year = %s AND quarter = %s
#         {f"AND LOWER(state_name) = %s" if state != "All" else ""}
#     """
#     params = [year, quarter]
#     if state != "All":
#         params.append(state.lower())

#     df_sql = pd.read_sql_query(query, conn, params=params)
#     conn.close()

#     df_sql['state_name'] = df_sql['state_name'].str.strip().str.lower()
#     df_sql['district_name'] = df_sql['district_name'].str.strip().str.lower()
#     return df_sql

# # === STEP 3: Merge SQL + CSV ===
# def merge_data(df_sql, df_csv):
#     merged = pd.merge(df_sql, df_csv, on=['state_name', 'district_name'], how='inner')
#     return merged

# # === STREAMLIT UI ===
# st.set_page_config(page_title="PhonePe Map Dashboard", layout="wide")

# st.title("🗺️ PhonePe Transaction Map (District-Level)")
# st.markdown("Filter data and view interactive 2D/3D map")

# # Filters
# col1, col2, col3 = st.columns(3)
# with col1:
#     year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023])
# with col2:
#     quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])
# with col3:
#     state = st.selectbox("Select State", ["All", "andhra pradesh", "tamil nadu", "maharashtra", "karnataka", "uttar pradesh", "west bengal", "kerala", "bihar", "delhi", "gujarat", "madhya pradesh"])  # Add more as needed

# # Map toggle
# view_mode = st.radio("Map Mode", ["2D", "3D"], horizontal=True)

# # === Run Queries + Display Map ===
# df_csv = load_csv_with_latlon()
# df_sql = fetch_postgres_data(state, year, quarter)

# if df_sql.empty:
#     st.warning("No data available for the selected filters.")
# else:
#     df_merged = merge_data(df_sql, df_csv)

#     # Apply formatting for hover tooltip
#     df_merged['Amount (Formatted)'] = df_merged['amount'].apply(format_indian_currency)

#     # === Plotly Map ===
#     fig = px.scatter_mapbox(
#         df_merged,
#         lat="latitude",
#         lon="longitude",
#         color="amount",
#         size="transaction_count",
#         size_max=40,
#         color_continuous_scale="YlOrRd",
#         hover_name="district_name",
#         hover_data={
#             "state_name": True,
#             "district_name": False,
#             "transaction_count": True,
#             "Amount (Formatted)": True,
#             "latitude": False,
#             "longitude": False
#         },
#         zoom=4,
#         height=700
#     )

#     fig.update_layout(mapbox_style="carto-positron")

#     if view_mode == "3D":
#         fig.update_traces(marker=dict(sizemode="area", opacity=0.8))
#     else:
#         fig.update_traces(marker=dict(sizemode="diameter", opacity=0.6))

#     fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#     st.plotly_chart(fig, use_container_width=True)

#it works but no multi-select & peak as heatmaps

# import streamlit as st
# import pandas as pd
# import pydeck as pdk
# import os

# # Set the page configuration
# st.set_page_config(layout="wide", page_title="📍 India Transaction Overview Map")
# st.title("📍 India Transaction Overview Map")

# # === 📄 Load the cleaned hover data ===
# CSV_PATH = "map_transaction_hover.csv" 

# # ✅ Step 1: Load and validate the CSV file
# if not os.path.exists(CSV_PATH):
#     st.error(f"❌ CSV file not found at path: {CSV_PATH}. Please make sure the file is in the same directory as your script.")
#     st.stop()

# df = pd.read_csv(CSV_PATH)

# # ✅ Define required columns and check their presence
# required_columns = [
#     "state", "district", "transaction_count",
#     "transaction_amount", "latitude", "longitude"
# ]

# if not all(col in df.columns for col in required_columns):
#     st.error("❌ The CSV file is missing one or more required columns.")
#     st.write("Expected columns:", required_columns)
#     st.write("Available columns:", df.columns.tolist())
#     st.stop()
    
# # Drop rows with missing lat/lon data to prevent errors
# df.dropna(subset=['latitude', 'longitude'], inplace=True)

# # ✅ Rename columns for consistency
# df = df.rename(columns={
#     "state": "state_name",
#     "district": "district_name",
#     "transaction_count": "txn_count",
#     "transaction_amount": "transaction_amount_val"
# })

# # ⭐ NEW: Pre-format data for the tooltip
# # This creates new string columns with formatting, which is more reliable for tooltips.
# df['txn_count_str'] = df['txn_count'].apply(lambda x: f"{x:,}")
# df['amount_str'] = df['transaction_amount_val'].apply(lambda x: f"₹{x:,.2f}")


# # ✅ Normalize elevation based on transaction amount (for 3D effect)
# max_elevation = 50000 
# df["elevation"] = df["transaction_amount_val"] / df["transaction_amount_val"].max() * max_elevation

# # === 🎛️ Sidebar Filters ===
# with st.sidebar:
#     st.header("🔎 Filter Map Data")
#     min_amt = int(df["transaction_amount_val"].min())
#     max_amt = int(df["transaction_amount_val"].max())

#     selected_range = st.slider(
#         "Filter by Transaction Amount (₹)",
#         min_value=min_amt,
#         max_value=max_amt,
#         value=(min_amt, max_amt)
#     )

# filtered_df = df[
#     (df["transaction_amount_val"] >= selected_range[0]) &
#     (df["transaction_amount_val"] <= selected_range[1])
# ]

# if filtered_df.empty:
#     st.warning("No data available for the selected transaction amount range.")
#     st.stop()

# # ✅ Configure PyDeck Column Layer
# column_layer = pdk.Layer(
#     "ColumnLayer",
#     data=filtered_df,
#     get_position='[longitude, latitude]',
#     get_elevation='elevation',
#     get_fill_color='[255, 255, 0, 160]',
#     radius=2500,
#     elevation_scale=1,
#     pickable=True,
#     auto_highlight=True,
#     extruded=True,
# )

# # ✅ Define initial view state
# view_state = pdk.ViewState(
#     latitude=22.5,
#     longitude=78.9,
#     zoom=4,
#     pitch=45,
#     bearing=0
# )

# # ⭐ UPDATED: Tooltip configuration now uses the new pre-formatted columns
# tooltip = {
#     "html": """
#         <b>State:</b> {state_name}<br/>
#         <b>District:</b> {district_name}<br/>
#         <b>Transactions:</b> {txn_count_str}<br/>
#         <b>Amount:</b> {amount_str}
#     """,
#     "style": {
#         "backgroundColor": "steelblue",
#         "color": "white",
#         "fontFamily": '"Helvetica Neue", Arial, sans-serif',
#         "zIndex": "10000",
#         }
# }

# # ✅ Render the map using st.pydeck_chart
# st.pydeck_chart(pdk.Deck(
#     layers=[column_layer],
#     initial_view_state=view_state,
#     tooltip=tooltip,
#     map_style="mapbox://styles/mapbox/dark-v9"
# ))

# st.info("💡 Hover over the yellow peaks to see details for each district.")

# it also works fine v-2 (no year & q select)

# import streamlit as st
# import pandas as pd
# import pydeck as pdk
# import os

# # Set the page configuration
# st.set_page_config(layout="wide", page_title="📍 India Transaction Heatmap")
# st.title("📍 India Transaction Heatmap")

# # === 📄 Load the cleaned hover data ===
# CSV_PATH = "map_transaction_hover.csv"

# # ✅ Step 1: Load and validate the CSV file
# if not os.path.exists(CSV_PATH):
#     st.error(f"❌ CSV file not found at path: {CSV_PATH}. Please make sure the file is in the same directory as your script.")
#     st.stop()

# df = pd.read_csv(CSV_PATH)

# # ✅ Define required columns and check their presence
# required_columns = [
#     "state", "district", "transaction_count",
#     "transaction_amount", "latitude", "longitude"
# ]

# if not all(col in df.columns for col in required_columns):
#     st.error("❌ The CSV file is missing one or more required columns.")
#     st.stop()

# # Drop rows with missing lat/lon data
# df.dropna(subset=['latitude', 'longitude'], inplace=True)

# # ✅ Rename columns
# df = df.rename(columns={
#     "state": "state_name",
#     "district": "district_name",
#     "transaction_count": "txn_count",
#     "transaction_amount": "transaction_amount_val"
# })

# # ⭐ NEW: Add a safety check to ensure the amount column is numeric
# df['transaction_amount_val'] = pd.to_numeric(df['transaction_amount_val'], errors='coerce')
# df.dropna(subset=['transaction_amount_val'], inplace=True) # Drop rows where conversion failed

# # Pre-format data for the tooltip
# df['txn_count_str'] = df['txn_count'].apply(lambda x: f"{x:,}")
# df['amount_str'] = df['transaction_amount_val'].apply(lambda x: f"₹{x:,.2f}")

# # === 🎛️ Sidebar Filters ===
# st.sidebar.header("🔎 Filter Map Data")

# state_options = sorted(list(df['state_name'].unique()))
# selected_states = st.sidebar.multiselect(
#     "Select State(s)",
#     options=state_options,
#     default=state_options
# )

# # Filter the dataframe
# filtered_df = df[df['state_name'].isin(selected_states)].copy()

# if filtered_df.empty:
#     st.warning("No data available for the selected states. Please select at least one state.")
#     st.stop()

# # --- Visual Enhancements for Heatmap ---

# # ⭐ NEW: More robust elevation and color calculation
# min_amt = filtered_df['transaction_amount_val'].min()
# max_amt = filtered_df['transaction_amount_val'].max()
# max_elevation = 100000

# # Safely calculate elevation to prevent division by zero
# if max_amt > 0:
#     filtered_df['elevation'] = (filtered_df['transaction_amount_val'] / max_amt) * max_elevation
# else:
#     filtered_df['elevation'] = 0

# def get_color(amount, min_val, max_val):
#     if (max_val - min_val) == 0:
#         return [0, 0, 255, 160]
#     norm_amt = (amount - min_val) / (max_val - min_val)
#     red = int(255 * norm_amt)
#     blue = int(255 * (1 - norm_amt))
#     return [red, 50, blue, 160]

# filtered_df['color'] = filtered_df['transaction_amount_val'].apply(lambda x: get_color(x, min_amt, max_amt))

# # ✅ Configure PyDeck Column Layer
# column_layer = pdk.Layer(
#     "ColumnLayer",
#     data=filtered_df,
#     get_position='[longitude, latitude]',
#     get_elevation='elevation',
#     get_fill_color='color',
#     radius=8000,
#     elevation_scale=1,
#     pickable=True,
#     auto_highlight=True,
#     extruded=True,
# )

# # ✅ Define initial view state
# view_state = pdk.ViewState(
#     latitude=22.0,
#     longitude=79.0,
#     zoom=4.5,
#     pitch=50,
#     bearing=0
# )

# # ✅ Configure tooltip
# tooltip = {
#     "html": """
#         <b>State:</b> {state_name}<br/>
#         <b>District:</b> {district_name}<br/>
#         <b>Transactions:</b> {txn_count_str}<br/>
#         <b>Amount:</b> {amount_str}
#     """,
#     "style": {
#         "backgroundColor": "rgba(0,0,0,0.8)",
#         "color": "white",
#         "fontFamily": '"Helvetica Neue", Arial, sans-serif',
#     }
# }

# # ✅ Render the map
# st.pydeck_chart(pdk.Deck(
#     layers=[column_layer],
#     initial_view_state=view_state,
#     tooltip=tooltip,
#     # map_style="mapbox://styles/mapbox/dark-v9"
# ))

# st.info("💡 Map shows transaction data by district. Low transaction amounts are in **blue**, and high amounts are in **red**.")




import streamlit as st
import pandas as pd
import pydeck as pdk
from sqlalchemy import create_engine

## 1. PAGE AND DATABASE CONFIGURATION
# ===============================================
st.set_page_config(layout="wide", page_title="📍 India Transaction Heatmap")
st.title("📍 India Transaction Heatmap")

# Your PostgreSQL database connection details
DB_CONFIG = {
    "user": "postgres", "password": "1234", "host": "localhost",
    "port": "5432", "dbname": "postgres"
}
TABLE_NAME = 'map_transaction_hover'


## 2. DATA LOADING FROM POSTGRESQL
# ===============================================
@st.cache_data(ttl=600)
def load_data_from_db():
    """Connects to PostgreSQL and loads the transaction data."""
    try:
        db_url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        engine = create_engine(db_url)
        df = pd.read_sql_table(TABLE_NAME, engine)
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Load the data
df = load_data_from_db()

if df is None or df.empty:
    st.stop()
    
# ---
## 3. DATA PREPARATION
# ===============================================
# Drop rows with missing essential data
df.dropna(subset=['latitude', 'longitude', 'amount'], inplace=True)

# Rename columns from the database to match the rest of the script's expectations
df = df.rename(columns={
    # "db_column_name": "script_column_name"
    "amount": "transaction_amount_val",
    "transaction_count": "txn_count",
    "year": "Year",
    "quarter": "Quarter"
})

# Ensure the amount column is numeric
df['transaction_amount_val'] = pd.to_numeric(df['transaction_amount_val'], errors='coerce')
df.dropna(subset=['transaction_amount_val'], inplace=True)

# Pre-format data for the tooltip display
df['txn_count_str'] = df['txn_count'].apply(lambda x: f"{x:,}")
df['amount_str'] = df['transaction_amount_val'].apply(lambda x: f"₹{x:,.2f}")

# ---
## 4. SIDEBAR FILTERS
# ===============================================
st.sidebar.header("🔎 Filter Map Data")

state_options = sorted(list(df['state_name'].unique()))
selected_states = st.sidebar.multiselect("State(s)", options=state_options, default=state_options)

year_options = sorted(list(df['Year'].unique()))
selected_years = st.sidebar.multiselect("Year(s)", options=year_options, default=year_options)

quarter_options = sorted(list(df['Quarter'].unique()))
selected_quarters = st.sidebar.multiselect("Quarter(s)", options=quarter_options, default=quarter_options)

# ---
## 5. APPLY FILTERS
# ===============================================
filtered_df = df[
    (df['state_name'].isin(selected_states)) &
    (df['Year'].isin(selected_years)) &
    (df['Quarter'].isin(selected_quarters))
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ---
## 6. MAP VISUALIZATION LOGIC
# ===============================================
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

# Configure PyDeck Column Layer
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

# Define initial view state
view_state = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.5, pitch=50, bearing=0)

# Configure tooltip
tooltip = {
    "html": """
        <b>State:</b> {state_name}<br/>
        <b>District:</b> {district_name}<br/>
        <b>Transactions:</b> {txn_count_str}<br/>
        <b>Amount:</b> {amount_str}
    """,
    "style": {"backgroundColor": "rgba(0,0,0,0.8)", "color": "white"}
}

# Render the map
st.pydeck_chart(pdk.Deck(
    layers=[column_layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    # map_style="mapbox://styles/mapbox/dark-v9"
))

st.info("💡 Map shows transaction data by district. Low transaction amounts are in **blue**, and high amounts are in **red**.")