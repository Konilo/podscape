def get_podcast_details(db_connector, title):
    sql = f"""
    SELECT
        url, title,
        DATE(lastUpdate, 'unixepoch') as lastUpdate,
        link, dead,
        contentType, itunesId, originalUrl,
        itunesAuthor, itunesOwnerName,
        explicit, itunesType, generator,
        DATE(newestItemPubdate, 'unixepoch') as newestItemPubdate,
        language,
        DATE(oldestItemPubdate, 'unixepoch') as oldestItemPubdate,
        episodeCount, host, description,
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