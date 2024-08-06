import plotly.express as px
import feedparser as fp
from datetime import datetime
import polars as pl
import streamlit as st


def get_podcast_details(db_connector, id):
    sql = f"""
    SELECT
        title, link, language,
        DATE(newestItemPubdate, 'unixepoch') as newestItemPubdate,
        DATE(oldestItemPubdate, 'unixepoch') as oldestItemPubdate,
        episodeCount,
        host,
        itunesAuthor, itunesOwnerName,
        generator,
        TRIM(
            COALESCE(category1 || ', ', '') ||
            COALESCE(category2 || ', ', '') ||
            COALESCE(category3 || ', ', '') ||
            COALESCE(category4 || ', ', '') ||
            COALESCE(category5 || ', ', '') ||
            COALESCE(category6 || ', ', '') ||
            COALESCE(category7 || ', ', '') ||
            COALESCE(category8 || ', ', '') ||
            COALESCE(category9 || ', ', '') ||
            COALESCE(category10, '')
        , ', ') as categories,
        url
    FROM podcasts
    WHERE id = {id}
    """
    return db_connector.query(sql)


def get_podcast_cover(db_connector, id):
    sql = f"""
    SELECT imageUrl
    FROM podcasts
    WHERE id = {id}
    """
    return db_connector.query(sql)["imageUrl"][0]


@st.cache_data
def get_podcast_creations_over_time(_db_connector, time_unit):
    # The underscore in _db_connector tells streamlit not to hash this object (which can't be hashed)
    time_unit_formats = {
        "day": "%Y-%m-%d",
        "week": None,
        "month": "%Y-%m-01",
        "semester": None,
        "year": "%Y-01-01",
    }

    if time_unit not in time_unit_formats:
        raise ValueError(f"Invalid time_unit: {time_unit}. Must be one of {list(time_unit_formats.keys())}")

    if time_unit == "semester":
        sql = """
        SELECT
            CASE
                WHEN strftime('%m', DATE(oldestItemPubdate, 'unixepoch')) BETWEEN '01' AND '06' THEN strftime('%Y-01-01', DATE(oldestItemPubdate, 'unixepoch'))
                ELSE strftime('%Y-07-01', DATE(oldestItemPubdate, 'unixepoch'))
            END AS Semester,
            COUNT(*) AS "# podcasts created"
        FROM podcasts
        WHERE oldestItemPubdate IS NOT NULL
        GROUP BY 1
        """
    elif time_unit == "week":
        sql = """
        SELECT
            DATE(
                DATE(oldestItemPubdate, 'unixepoch'), '-' ||
                CASE strftime('%w', DATE(oldestItemPubdate, 'unixepoch'))
                    WHEN '0' THEN 6
                    ELSE strftime('%w', DATE(oldestItemPubdate, 'unixepoch')) - 1
                END || ' days'
            ) AS Week,
            COUNT(*) AS "# podcasts created"
        FROM podcasts
        WHERE oldestItemPubdate IS NOT NULL
        GROUP BY 1
        """
    else:
        strftime_format = time_unit_formats[time_unit]
        sql = f"""
        SELECT
            DATE(strftime(
                '{strftime_format}',
                DATE(oldestItemPubdate, 'unixepoch')
            )) AS {time_unit.capitalize()},
            COUNT(*) AS "# podcasts created"
        FROM podcasts
        WHERE oldestItemPubdate IS NOT NULL
        GROUP BY 1
        """

    df = _db_connector.query(sql)

    return px.line(
        df,
        x=time_unit.capitalize(),
        y="# podcasts created",
        title="Podcasts created over time",
        markers=False if (time_unit in ["day", "week", "month"]) else True,
    )


def parse_date(date_str):
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return "Parsing error"


def get_episode_infos(url):
    feed = fp.parse(url)

    df = pl.DataFrame(
        {
            "title": [entry["title"] for entry in feed["entries"]],
            "date": [parse_date(entry["published"]) for entry in feed["entries"]],
            "duration": [entry["itunes_duration"] for entry in feed["entries"]],
        }
    )

    return df


def get_ids_from_title(db_connector, title):
    simplified_title = title.lower().replace(" ", "").replace(",", "")
    sql = f"""
    SELECT id
    FROM podcasts
    WHERE replace(replace(lower(title), ' ', ''), ',', '') LIKE '%{simplified_title}%'
    """
    return db_connector.query(sql, "list")


def get_podcast_title(db_connector, id):
    sql = f"""
    SELECT title
    FROM podcasts
    WHERE id = {id}
    """
    return db_connector.query(sql)["title"][0]


def get_podcast_options(sqlite_connector, matching_podcast_ids):
    podcast_options = pl.DataFrame(
        {"id": [], "title": [], "cover_url": [], "title_for_selectbox": []},
        schema={
            "id": pl.Int64,
            "title": pl.Utf8,
            "cover_url": pl.Utf8,
            "title_for_selectbox": pl.Utf8,
        },
    )
    for index, podcast_id in enumerate(matching_podcast_ids):
        cover_url = get_podcast_cover(sqlite_connector, podcast_id)
        title = get_podcast_title(sqlite_connector, podcast_id)
        title_for_selectbox = f"{title} (match # {index + 1})"
        podcast_options = podcast_options.vstack(
            pl.DataFrame({"id": [podcast_id], "title": [title], "cover_url": [cover_url], "title_for_selectbox": [title_for_selectbox]})
        )

    return podcast_options
