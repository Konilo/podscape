import plotly.express as px


def get_podcast_details(db_connector, title):
    sql = f"""
    SELECT
        title, url, link, language,
        DATE(newestItemPubdate, 'unixepoch') as newestItemPubdate,
        DATE(oldestItemPubdate, 'unixepoch') as oldestItemPubdate,
        episodeCount, host, description,
        contentType, itunesId, originalUrl,
        itunesAuthor, itunesOwnerName,
        explicit, itunesType, generator,
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
        , ', ') as categories
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
    return db_connector.query(sql)['imageUrl'][0]

def get_podcast_creations_over_time(db_connector):
    sql = f"""
    SELECT
        DATE(strftime(
            '%Y-%m',
            DATE(oldestItemPubdate, 'unixepoch')
        ) || '-01') AS Month,
        COUNT(*) AS "# podcasts created"
    FROM podcasts
    WHERE oldestItemPubdate IS NOT NULL
    GROUP BY 1
    """
    df = db_connector.query(sql)
    return px.line(df, x='Month', y='# podcasts created', title='Podcasts created over time')
