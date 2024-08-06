import plotly.express as px
import feedparser as fp
from datetime import datetime
import polars as pl
import streamlit as st


def get_podcast_details(db_connector, title):
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
    where title = '{title}'
    """
    return db_connector.query(sql)


def get_podcast_cover(db_connector, title):
    sql = f"""
    SELECT imageUrl
    FROM podcasts
    where title = '{title}'
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
        "year": "%Y-01-01"
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
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S %z',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return "Parsing error"


def get_episode_infos(url):
    feed = fp.parse(url)

    df = pl.DataFrame({
        "title": [entry["title"] for entry in feed["entries"]],
        "date": [parse_date(entry["published"]) for entry in feed["entries"]],
        "duration": [entry["itunes_duration"] for entry in feed["entries"]],
    })

    return df
