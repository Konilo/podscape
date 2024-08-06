import streamlit as st
from utils.sqlite_connector import SqliteConnector
from utils.utils import get_podcast_details, get_podcast_cover, get_podcast_creations_over_time, get_episode_infos

TIME_UNITS = ["day", "week", "month", "semester", "year"]

# Setup
db_file_path = "podscape/data/podcastindex_feeds.db"
sqlite_connector = SqliteConnector(db_file_path)

# Page title
st.write("# Podscape")

# Sidebar
st.sidebar.header("Filters")


def text_input(label, default_value):
    return st.sidebar.text_input(label, default_value)


podcast_name = text_input("Podcast name", "Today, Explained")


def selectbox(label, options, default_index=0):
    return st.sidebar.selectbox(label, options, default_index)


time_unit = selectbox("Time unit", TIME_UNITS, 3)

# Body
## Podcast details
st.subheader("Podcast Details")
df = get_podcast_details(sqlite_connector, podcast_name)
if df.shape[0] == 0:
    st.write("Podcast not found")
else:
    if df.shape[0] == 1:
        cover_url = get_podcast_cover(sqlite_connector, podcast_name)
        st.image(cover_url, width=200)
    st.dataframe(df)
    if df.shape[0] == 1:
        # TODO use podcast_name instead of df['url'][0]
        ep_infos = get_episode_infos(df["url"][0])
        st.dataframe(ep_infos)

## N podcast creations over time
st.subheader("Podcasts created over time")
fig = get_podcast_creations_over_time(sqlite_connector, time_unit)
st.plotly_chart(fig)
