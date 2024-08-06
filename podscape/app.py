import streamlit as st
from utils.sqlite_connector import SqliteConnector
from utils.utils import (
    get_podcast_details,
    get_podcast_cover,
    get_podcast_creations_over_time,
    get_episode_infos,
    get_ids_from_title,
    get_podcast_options,
)
import polars as pl

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
    matching_podcast_ids = get_ids_from_title(sqlite_connector, podcast_name)

    if len(matching_podcast_ids) == 0:
        st.write("Podcast not found")
    else:
        if len(matching_podcast_ids) > 1:
            st.write("Multiple podcasts found. Please select the correct one.")
            podcast_options = get_podcast_options(sqlite_connector, matching_podcast_ids)
            
            for row in podcast_options.iter_rows(named=True):
                if row["cover_url"] != "":
                    st.image(row["cover_url"], width=100, caption=row["title_for_selectbox"])
                else:
                    st.write(f"{row["title_for_selectbox"]} (no cover image available)")

            selected_podcast_index = selectbox(
                "Select a podcast",
                podcast_options["title_for_selectbox"].to_list(),
            )
            matching_podcast_ids = podcast_options.filter(
                pl.col("title_for_selectbox") == selected_podcast_index
            )["id"].to_list()

        cover_url = get_podcast_cover(sqlite_connector, matching_podcast_ids[0])
        st.image(cover_url, width=200)
        df = get_podcast_details(sqlite_connector, matching_podcast_ids[0])
        st.dataframe(df)
        ep_infos = get_episode_infos(df["url"][0])
        st.dataframe(ep_infos)

## Podcast landscape tab
with landscape_tab:
    st.subheader("Podcasts created over time")
    time_unit = selectbox("Time unit", TIME_UNITS, 3)
    fig = get_podcast_creations_over_time(sqlite_connector, time_unit)
    st.plotly_chart(fig)
