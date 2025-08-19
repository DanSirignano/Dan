"""
Name:       Dan Sirignano
CS 230:     Summer Section 1
Data:       Shipwreck Data
URL:        https://dansirignanotabrepositories-hvbomd4sqfgzdim7exa8et.streamlit.app/

Description:

This program aims to answer some questions about the Shipwreck Data we're provided.
Going in order, this program breaks down the shipwrecks by each vessel type,
shows the user the oldest wreck of the data, it shows the average lifespans
of the shipwrecks over time, shows the user a shipwreck locations map, in which
the user can user the numeric sliders to alter the casualty/year ranges of the ships,
it shows a pivot table connecting the type of vessel to the number of lives lost in
the wreck, it shows the max casualties of any wreck, and lastly shows the user the
shipwrecks based on the cause of the wreck.

References:
https://brightspace.bentley.edu/d2l/le/lessons/44441/topics/935918
https://docs.streamlit.io/develop/tutorials
https://streamlitpython.com
https://github.com/streamlit/streamlit
https://brightspace.bentley.edu/d2l/le/lessons/44441/topics/935918
https://www.youtube.com/watch?v=8G4cD7ofgCM&ab_channel=cissandbox
https://www.youtube.com/playlist?list=PLMi6KgK4_mk2rK5jD-BK5RigFIP2QSq8W

"""

# Import the libraries first
import pandas as pd
import streamlit as st
import numpy as np
import pydeck as pdk

df = pd.read_csv("Shipwreck Database.csv")  # Load dataset from CSV

# Convert columns to numerics where needed (and errors using coerce, so blanks/invalid data is NaN not a number
df['YEAR'] = pd.to_numeric(df['YEAR'], errors = 'coerce')
df['YEAR BUILT'] = pd.to_numeric(df['YEAR BUILT'], errors = 'coerce')

# Calculating lifespan of each ship, difference between year lost and year built
df['Lifespan'] = df['YEAR'] - df['YEAR BUILT']  #[COLUMNS] add a calculated column

# Convert coordinates to numerics, latitude/longitudes for maps
df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors = 'coerce')
df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors = 'coerce')

# Convert casualties to numerics
df['LIVES LOST'] = pd.to_numeric(df['LIVES LOST'], errors = 'coerce')

# First Function

def get_oldest_by_type(dataframe, vessel_type='All'):  #[FUNC2P] function with 2 or more parameters, default value
# Function to return the oldest shipwreck based on the vessel type
# If all, then it looks at the entire dataset, otherwise can filter a certain vessel
    if vessel_type != 'All':
        filtered = dataframe[dataframe['VESSEL TYPE'] == vessel_type]  #[FILTER1] filtering by 1 condition
    else:
        filtered = dataframe
    oldest_year = filtered['YEAR'].min()  #[MAXMIN] find min value, earliest year
    return filtered[filtered['YEAR'] == oldest_year], oldest_year  # #[FUNCRETURN2] returns 2 values
                                    # Returns the rows matching the oldest year

# Streamlit Widgets

st.sidebar.title("Shipwreck Modifier")  #[ST3] use of sidebar feature
# Title of sidebar is Shipwreck Modifier
# Create dropdown list of vessel types plus all at the top, as default
vessel_types = ['All'] + sorted(df['VESSEL TYPE'].dropna().astype(str).unique().tolist())
selected_type = st.sidebar.selectbox("Select Vessel Type:", vessel_types)  #[ST1] dropdown box
# This dropdown allows you to select the type otherwise

# Slider to pick maximum year (filters ships that happened before/at the chosen year)
max_year = st.sidebar.slider(
    "Select Maximum Year Lost:",
    int(df['YEAR'].min()), # Min year found in dataset
    int(df['YEAR'].max()),  # Max year found in dataset
    int(df['YEAR'].max())  # Defaults to max year
)  #[ST2] slider widget

# This is info text for the side bar
st.sidebar.markdown("Use the controls above to filter the shipwreck dataset as you go.")

# Give a vessel type filter
filtered_df = df[df['VESSEL TYPE'] == selected_type] if selected_type != 'All' else df.copy()

# Filter for the year of the vessel
filtered_df = filtered_df[filtered_df['YEAR'] <= max_year]  #[FILTER2] filter by 2 conditions when combined above

# Sort by years in ascending order
filtered_df = filtered_df.sort_values(by="YEAR", ascending = True)  #[SORT] sort ascending order


st.title("Shipwreck Data Set Information")   # Title info
st.write("This web app visualizes shipwrecks' data to help users explore different info trends.")

# Get oldest wreck in selection and across the original dataset
oldest_df, oldest_year = get_oldest_by_type(filtered_df, selected_type)  #[FUNCCALL2] function call
all_oldest_df, all_oldest_year = get_oldest_by_type(df)  # #[FUNCCALL2] function called again


# Chart 1: Bar chart of shipwrecks based on the vessel type

st.subheader("Shipwrecks by Vessel Type")

# Count shipwrecks according to each vessel type
type_counts = filtered_df['VESSEL TYPE'].value_counts()

# Keeping only the top 30 vessel types to simplify, put the remaining into "Other"
top_n = 30
if len(type_counts) > top_n:
    top_types = type_counts.head(top_n)   # Get top n element
    other_count = type_counts.iloc[top_n:].sum()   # Sum up counts of the other types
    type_counts = pd.concat([top_types, pd.Series({"Other": other_count})])  # Combine together

# Display as  horizontal bar chart and sort to make it easier to see
st.bar_chart(type_counts.sort_values())  #[CHART1] bar chart


# Oldest Wreck Info

st.subheader("Date of Oldest Wreck in Data")
st.write(f"The year of the oldest wreck in the selected group is: {oldest_year:.0f}")
st.dataframe(oldest_df)


# Chart 2: Lifespan over time of ships

st.subheader("Average Lifespan of Shipwrecks Over Time") # Add sub header to interface
st.write("Here is the average lifespan of the ships (before becoming wrecks) over time.")
# Drop rows where lifespan/year data is missing
lifespan_df = filtered_df.dropna(subset = ['Lifespan', 'YEAR'])  # Pandas dataframe, remove rows that don't have values for Lifespan or Year

# Group them by the decade to see it easier
lifespan_df['Decade'] = (lifespan_df['YEAR'] // 10) * 10  # New column decade, grouping year data into groups of 10 years
                                            # // floor division, returns integer/rounds down to whole number
# Calc average lifespan per decade, round to 1 decimal
avg_lifespan = lifespan_df.groupby('Decade')['Lifespan'].mean().round(1)

# Show a line chart of average ship lifespans
st.line_chart(avg_lifespan)  #[CHART2] different chart type (line)
        # Use streamlit's line chart to display it

# Map Visuals and User Interaction

st.subheader("Shipwreck Locations Map")
st.markdown("### Filter Map by Casualty Count & Year Range")

# Casualty filter range based on minimum/max casualties in a wreck in the data
min_casualties = int(df['LIVES LOST'].min(skipna=True))
max_casualties = int(df['LIVES LOST'].max(skipna=True))

casualty_range = st.slider(
    "Select casualty range to display on map:",
    min_casualties, max_casualties, (min_casualties, max_casualties)
)

# Year range filter on the map
year_min = int(df['YEAR'].min())
year_max = int(df['YEAR'].max())
year_range = st.slider(
    "Select year range:",
    year_min, year_max, (year_min, year_max)
)

# Filter map dataset if it has coordinates/casualties/year data
map_df = filtered_df.dropna(subset=['LATITUDE', 'LONGITUDE', 'LIVES LOST', 'YEAR'])
map_df = map_df[
    (map_df['LIVES LOST'] >= casualty_range[0]) &
    (map_df['LIVES LOST'] <= casualty_range[1]) &
    (map_df['YEAR'] >= year_range[0]) &
    (map_df['YEAR'] <= year_range[1])   #[FILTER2] filter data by two or more conditions
]

# If no data is matching, tell the user
if map_df.empty:
    st.warning("No shipwrecks match the filters. Try adjusting the casualty or year range.")
else:
    # Scatterplot layer for the shipwrecks
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[LONGITUDE, LATITUDE]',   # Given coordinates
        get_radius=5000,   # Marker size
        get_fill_color=[200, 30, 0, 160],  # Color choice
        pickable=True,   # Hover tooltips there
    )

    # Map view centered on average latitude/longitude of the filtered data
    view_state = pdk.ViewState(
        latitude=map_df['LATITUDE'].mean(),
        longitude=map_df['LONGITUDE'].mean(),
        zoom=3
    )

    # Build deck.gl chart/render with the tooltip
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{SHIPS NAME} | Year Lost: {YEAR} | Lives Lost: {LIVES LOST}"}
    )

    st.pydeck_chart(r)  #[MAP] custom interactive map


# Pivot Table

st.subheader("Pivot Table Vessel / Casualties Summary")

# Average casualties per vessel type
pivot = filtered_df.pivot_table(index='VESSEL TYPE', values='LIVES LOST', aggfunc='mean')
# Rounding averages to 1 decimal place for easy viewing
pivot = pivot.round(1)
st.dataframe(pivot)  #[PIVOTTABLE] pivot table


# Max / Min

st.write("## Max Casualties")
st.write("This is the maximum number of casualties in one shipwreck for this group of data.")
# Get value of max casualties
max_casualties = filtered_df['LIVES LOST'].max()  #[MAXMIN] max value
if pd.notna(max_casualties):
    st.write(int(max_casualties))  # show as integer
else:
    st.write("No data available")


# Cause of Loss Analysis

st.subheader("Shipwrecks by Cause of Loss")

# Count number of wrecks based on cause of loss
cause_counts = filtered_df['CAUSE OF LOSS'].value_counts(dropna = False)

# Replace NaN phrasing with "Unknown" so missing values show up clearer
cause_counts.index = [x if pd.notna(x) else "Unknown" for x in cause_counts.index]  #[LISTCOMP] list comprehension

# Only keep the top 30 and group the rest as other to make it easier to see
top_n = 30
if len(cause_counts) > top_n:
    top_causes = cause_counts.head(top_n)    # Take top n element causes
    other_count = cause_counts.iloc[top_n:].sum()   # Sum up remainder
    cause_counts = pd.concat([top_causes, pd.Series({"Other": other_count})])

# Display it as as horizontal bar chart with sorting
st.bar_chart(cause_counts.sort_values())  #[CHART1] reused bar chart type
