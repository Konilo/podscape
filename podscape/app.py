import streamlit as st
from utils.sqlite_connector import SqliteConnector
from utils.utils import get_podcast_details, get_podcast_cover, get_podcast_creations_over_time, get_episode_infos

TIME_UNITS = ["day", "week", "month", "semester", "year"]

# Setup
db_file_path = "podscape/data/podcastindex_feeds.db"
sqlite_connector = SqliteConnector(db_file_path)

def text_input(label, default_value):
    return st.text_input(label, default_value)


def selectbox(label, options, default_index=0):
    return st.selectbox(label, options, default_index)

# Page title
st.write("# Podscape")

# Body
details_tab, landscape_tab = st.tabs(["Podcast details", "Podcast landscape"])
## Podcast details tab
with details_tab:
    st.subheader("Podcast Details")
    podcast_name = text_input("Podcast name", "Today, Explained")
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

## Podcast landscape tab
with landscape_tab:
    st.subheader("Podcasts created over time")
    time_unit = selectbox("Time unit", TIME_UNITS, 3)
    fig = get_podcast_creations_over_time(sqlite_connector, time_unit)
    st.plotly_chart(fig)
