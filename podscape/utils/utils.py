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
        title=f"Podcasts creations per {time_unit}",
        markers=False if (time_unit in ["day", "week", "month"]) else True,
    )


@st.cache_data
def get_podcast_ids_from_title(_db_connector, title, exact_match):
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


@st.cache_data
def get_podcasts_per_host_day_df(_db_connector):
    sql = """
    SELECT date, host as Host, "# podcasts created"
    FROM podcasts_per_host_day
    """
    return _db_connector.query(sql)


def get_podcasts_per_host_pie(_db_connector, start_date, end_date, threshold=100000):
    df = get_podcasts_per_host_day_df(_db_connector)
    df = df.filter((pl.col("date") >= start_date) & (pl.col("date") <= end_date))
    df = df.group_by("Host").agg(pl.sum("# podcasts created"))
    df = pl.concat(
        [
            df.filter(pl.col("# podcasts created") >= threshold),
            pl.DataFrame(
                {"Host": ["others"], "# podcasts created": [df.filter(pl.col("# podcasts created") < threshold)["# podcasts created"].sum()]}
            ),
        ]
    )
    return px.pie(
        df,
        names="Host",
        values="# podcasts created",
        title=f"Podcast creations per host ({start_date} to {end_date})",
    )


def get_podcasts_per_host_time_bar(_db_connector, start_date, end_date, time_unit, threshold=10000):
    df = get_podcasts_per_host_day_df(_db_connector)
    df = df.filter((pl.col("date") >= start_date) & (pl.col("date") <= end_date))

    if time_unit == "day":
        df = df.with_columns(pl.col("date").alias(time_unit.capitalize()))
    elif time_unit == "week":
        df = df.with_columns(pl.col("date").dt.truncate("1w").alias(time_unit.capitalize()))
    elif time_unit == "month":
        df = df.with_columns(pl.col("date").dt.truncate("1mo").alias(time_unit.capitalize()))
    elif time_unit == "semester":
        df = df.with_columns(((pl.col("date").dt.year() * 2 + (pl.col("date").dt.month() - 1) // 6).cast(pl.Utf8)).alias(time_unit.capitalize()))
    elif time_unit == "year":
        df = df.with_columns(pl.col("date").dt.truncate("1y").alias(time_unit.capitalize()))
    else:
        raise ValueError("Unsupported time unit. Choose from 'day', 'week', 'month', 'semester', 'year'.")
    df = df.drop("date")

    df = df.group_by(time_unit.capitalize(), "Host").agg(pl.sum("# podcasts created").alias("# podcasts created"))

    # Apply threshold
    df_above_threshold = df.filter(pl.col("# podcasts created") >= threshold)
    df_below_threshold = df.filter(pl.col("# podcasts created") < threshold)

    if df_below_threshold.shape[0] > 0:
        df_others = (
            df_below_threshold.group_by(time_unit.capitalize())
            .agg(pl.sum("# podcasts created").alias("# podcasts created"))
            .with_columns(pl.lit("others").alias("Host"))
            .select([time_unit.capitalize(), "Host", "# podcasts created"])
        )

        df = pl.concat([df_above_threshold, df_others])
    else:
        df = df_above_threshold

    df = df.sort(by="# podcasts created", descending=True)

    return px.bar(
        df,
        x=time_unit.capitalize(),
        y="# podcasts created",
        color="Host",
        title=f"Podcast creations per host per {time_unit} ({start_date} to {end_date})",
    )
