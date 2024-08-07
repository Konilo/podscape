import plotly.express as px
import polars as pl
import streamlit as st

from .pod_class import PodClass


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


@st.cache_data
def get_podcast_ids_from_title(_db_connector, title, exact_match):
    # Underscore in _db_connector: idem
    if exact_match:
        where_clause = f"title = '{title}'"
    else:
        simplified_title = title.lower().replace(" ", "").replace(",", "")
        where_clause = f"replace(replace(lower(title), ' ', ''), ',', '') LIKE '%{simplified_title}%'"
    sql = f"""
    SELECT id
    FROM podcasts
    WHERE {where_clause}
    """
    return _db_connector.query(sql, "list")


@st.cache_data
def get_podcast_options(_db_connector, matching_podcast_ids):
    # Underscore in _db_connector: idem
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
        pod_object = PodClass(_db_connector, podcast_id)
        cover_url = pod_object.get_info("imageUrl")
        title = pod_object.get_info("title")
        title_for_selectbox = f"{title} (match # {index + 1})"
        podcast_options = podcast_options.vstack(
            pl.DataFrame({"id": [podcast_id], "title": [title], "cover_url": [cover_url], "title_for_selectbox": [title_for_selectbox]})
        )

    return podcast_options
