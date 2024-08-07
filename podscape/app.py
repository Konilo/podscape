import streamlit as st
import polars as pl

from utils.sqlite_connector import SqliteConnector
from utils.utils import (
    get_podcast_creations_over_time,
    get_podcast_ids_from_title,
    get_podcast_options,
)
from utils.pod_class import PodClass


TIME_UNITS = ["day", "week", "month", "semester", "year"]

# Setup
db_file_path = "podscape/data/podcastindex_feeds.db"
sqlite_connector = SqliteConnector(db_file_path)

# Page title
st.write("# Podscape")

# Body
details_tab, landscape_tab = st.tabs(["Podcast details", "Podcast landscape"])

## Podcast details tab
with details_tab:
    with st.expander("Search for a podcast", expanded=True):
        podcast_name = st.text_input("Podcast name", "Today, Explained")
        matching_podcast_ids = get_podcast_ids_from_title(sqlite_connector, podcast_name)

        # No podcast found
        if len(matching_podcast_ids) == 0:
            st.write("Podcast not found")
        else:
            # Multiple podcasts found
            if len(matching_podcast_ids) > 1:
                st.write("Multiple podcasts found. Please select the correct one.")
                podcast_options = get_podcast_options(sqlite_connector, matching_podcast_ids)
                
                columns = st.columns(3)
                index = 0
                for row in podcast_options.iter_rows(named=True):
                    if row["cover_url"] != "":
                        columns[index].image(row["cover_url"], width=100, caption=row["title_for_selectbox"])
                    else:
                        columns[index].write(f"{row["title_for_selectbox"]} (no cover image available)")
                    if index < 2:
                        index += 1
                    else:
                        index = 0

                selected_podcast_index = st.selectbox(
                    "Select a podcast",
                    podcast_options["title_for_selectbox"].to_list(),
                    label_visibility="collapsed",
                )
                matching_podcast_ids = podcast_options.filter(
                    pl.col("title_for_selectbox") == selected_podcast_index
                )["id"].to_list()

    podcast_object = PodClass(sqlite_connector, matching_podcast_ids[0])
    cover_url = podcast_object.get_info("imageUrl")
    st.image(cover_url, width=200)
    df = podcast_object.get_details()
    st.dataframe(df)
    ep_infos = podcast_object.get_episode_infos()
    st.dataframe(ep_infos)

## Podcast landscape tab
with landscape_tab:
    st.subheader("Podcasts created over time")

    with st.expander("Select a time unit", expanded=True):
        time_unit = st.selectbox("Time unit", TIME_UNITS, 3)
    
    fig = get_podcast_creations_over_time(sqlite_connector, time_unit)
    st.plotly_chart(fig)
