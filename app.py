import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect("polling_data.db", check_same_thread=False)
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS polling_data (
                serial INTEGER PRIMARY KEY,
                locality TEXT,
                building TEXT,
                area TEXT,
                voter_type TEXT,
                bjp_2017 INTEGER,
                congress_2017 INTEGER,
                bjp_2022 INTEGER,
                congress_2022 INTEGER
            )''')
conn.commit()

# Function to insert or update polling station data
def update_station(serial, locality, building, area, voter_type, bjp_2017, congress_2017, bjp_2022, congress_2022):
    # Check if record exists
    c.execute("SELECT * FROM polling_data WHERE serial = ?", (serial,))
    data = c.fetchone()
    
    if data:
        # Update existing record
        c.execute('''UPDATE polling_data SET locality=?, building=?, area=?, voter_type=?, 
                     bjp_2017=?, congress_2017=?, bjp_2022=?, congress_2022=? WHERE serial=?''',
                  (locality, building, area, voter_type, bjp_2017, congress_2017, bjp_2022, congress_2022, serial))
    else:
        # Insert new record
        c.execute('''INSERT INTO polling_data (serial, locality, building, area, voter_type, 
                     bjp_2017, congress_2017, bjp_2022, congress_2022)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (serial, locality, building, area, voter_type, bjp_2017, congress_2017, bjp_2022, congress_2022))
    
    conn.commit()

# Function to load all polling data
def load_data():
    df = pd.read_sql_query("SELECT * FROM polling_data", conn)
    return df

# Streamlit UI
st.title("🗳️ Polling Station Voting Data")

# ✅ **Form to Add or Update Data**
st.subheader("📌 Add or Update Polling Station Data")
col1, col2 = st.columns(2)

with col1:
    serial = st.number_input("Serial Number", min_value=1, value=1, step=1)
    locality = st.text_input("Locality", value=f"Polling Station {serial}")
    building = st.text_input("Building", value=f"Govt. School {serial}")

with col2:
    area = st.text_input("Area", value=f"Area {serial}")
    voter_type = st.selectbox("Voter Type", ["For All", "Men Only", "Women Only"])
    bjp_2017 = st.number_input("Votes for BJP (2017)", min_value=0, value=0, step=1)
    congress_2017 = st.number_input("Votes for Congress (2017)", min_value=0, value=0, step=1)
    bjp_2022 = st.number_input("Votes for BJP (2022)", min_value=0, value=0, step=1)
    congress_2022 = st.number_input("Votes for Congress (2022)", min_value=0, value=0, step=1)

if st.button("Save Data"):
    update_station(serial, locality, building, area, voter_type, bjp_2017, congress_2017, bjp_2022, congress_2022)
    st.success(f"✅ Data saved successfully for {locality} (Serial {serial})")

# 🔍 **Search by Locality**
st.subheader("🔎 Search Polling Station by Locality")
search_query = st.text_input("Enter Locality Name:")

if search_query:
    query = "SELECT * FROM polling_data WHERE locality LIKE ?"
    df_search = pd.read_sql_query(query, conn, params=("%" + search_query + "%",))
    
    if not df_search.empty:
        st.write(df_search)  # Display table
    else:
        st.warning("❌ No matching polling station found.")

# 📊 **Compare Votes & Generate Chart**
if search_query and not df_search.empty:
    st.subheader("📊 Vote Comparison (BJP vs Congress)")
    
    # Extract data for visualization
    labels = ["BJP 2017", "Congress 2017", "BJP 2022", "Congress 2022"]
    values = [
        df_search["bjp_2017"].sum(),
        df_search["congress_2017"].sum(),
        df_search["bjp_2022"].sum(),
        df_search["congress_2022"].sum(),
    ]

    # Generate Bar Chart
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=["blue", "red", "blue", "red"])
    ax.set_ylabel("Votes")
    ax.set_title(f"Vote Trend in {search_query}")

    st.pyplot(fig)

# 📋 **Show All Polling Stations**
if st.checkbox("📋 Show All Polling Stations"):
    df_all = load_data()
    st.dataframe(df_all)  # Display full table

# Close database connection
conn.close()
