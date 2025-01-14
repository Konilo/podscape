import streamlit as st
import polars as pl
from datetime import date

from utils.sqlite_connector import SqliteConnector
from utils.utils import (
    get_podcast_creations_over_time,
    get_podcast_ids_from_title,
    get_podcast_options,
    get_podcasts_per_host_pie,
    get_podcasts_per_host_time_bar,
)
from utils.pod_class import PodClass


TIME_UNITS = ["day", "week", "month", "semester", "year"]
MAX_PODCAST_OPTIONS = 15

# Setup
st.set_page_config(
    page_title="Podscape",
    page_icon=":loud_sound:",
)
db_file_path = "podscape/data/podcastindex_feeds.db"
sqlite_connector = SqliteConnector(db_file_path)


# Page title

st.title(":loud_sound: :blue[Podscape]")

# Body
details_tab, landscape_tab = st.tabs([":mag: Podcast details", ":bar_chart: Podcasting landscape"])

## Podcast details tab
with details_tab:
    with st.expander("Search for a podcast", expanded=True):
        podcast_title = st.text_input("Podcast title", "Today, Explained")
        exact_match = st.checkbox("Exact title match", value=True)
        matching_podcast_ids = get_podcast_ids_from_title(sqlite_connector, podcast_title, exact_match)

        # No podcast found
        if len(matching_podcast_ids) == 0:
            st.write("Podcast not found")
        else:
            # Multiple podcasts found
            if len(matching_podcast_ids) > 1:
                if len(matching_podcast_ids) < MAX_PODCAST_OPTIONS + 1:
                    st.write("Multiple podcasts found. Please select the correct one.")
                else:
                    st.write(
                        f"{len(matching_podcast_ids)} podcasts found, only showing the first {MAX_PODCAST_OPTIONS}. Please refine your search or refine your search."
                    )
                podcast_options = get_podcast_options(sqlite_connector, matching_podcast_ids[:MAX_PODCAST_OPTIONS])

                columns = st.columns(3)
                index = 0
                for row in podcast_options.iter_rows(named=True):
                    columns[index].image(row["cover_url"], width=100, caption=row["title_for_selectbox"])
                    if index < 2:
                        index += 1
                    else:
                        index = 0

                selected_podcast_index = st.selectbox(
                    "Select a podcast",
                    podcast_options["title_for_selectbox"].to_list(),
                    label_visibility="collapsed",
                )
                matching_podcast_ids = podcast_options.filter(pl.col("title_for_selectbox") == selected_podcast_index)["id"].to_list()

    ### Overview
    st.subheader("Overview")
    podcast_object = PodClass(sqlite_connector, matching_podcast_ids[0])
    cover_col, infos_col = st.columns([0.3, 0.7], vertical_alignment="center")
    with cover_col:
        cover_url = podcast_object.get_info("imageUrl")
        st.image(cover_url, width=200)
    with infos_col:
        with st.container(border=True):
            st.write(f"**Title:** {podcast_object.get_info('title')}")
            st.write(f"**Author:** {podcast_object.get_info('itunesAuthor')}")
            st.write(f"**Language:** {podcast_object.get_info('language')}")
            st.write(f"**Categories:** {podcast_object.get_info('categories')}")
            st.write(f"**Link:** {podcast_object.get_info('link')}")
            st.write(f"**Feed:** {podcast_object.get_info('url')}")

    ### Episodes
    st.subheader("Episodes")
    ep_infos = podcast_object.get_episode_infos()
    st.dataframe(
        ep_infos,
        width=705,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn(),
            "duration": st.column_config.NumberColumn(format="%d min"),
        },
    )

## Podcasting landscape tab
with landscape_tab:
    ### Podcast creations
    st.subheader("Podcast creations")
    with st.expander("Options", expanded=True):
        time_unit_creations = st.selectbox("Time unit", TIME_UNITS, 4, key="time_unit_creations")
    podcast_creations_over_time = get_podcast_creations_over_time(sqlite_connector, time_unit_creations)
    st.plotly_chart(podcast_creations_over_time)

    ### Podcasts per host
    st.subheader("Hosting platforms")
    with st.expander("Options", expanded=True):
        time_unit_hosts = st.selectbox("Time unit", TIME_UNITS, 4, key="time_unit_hosts")
        start_date = st.date_input("Start", value=date(2002, 10, 1))
        end_date = st.date_input("End", value=date.today())
    podcasts_per_host_pie = get_podcasts_per_host_pie(sqlite_connector, start_date, end_date)
    st.plotly_chart(podcasts_per_host_pie)
    podcasts_per_host_time_bar = get_podcasts_per_host_time_bar(sqlite_connector, start_date, end_date, time_unit_hosts)
    st.plotly_chart(podcasts_per_host_time_bar)
