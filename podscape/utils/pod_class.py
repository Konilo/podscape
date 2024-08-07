import logging
from datetime import datetime

import polars as pl
import feedparser as fp


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PodClass:
    """A class to get information about a podcast"""
    def __init__(self, db_connector, id):
        self.db_connector = db_connector
        self.id = id
        self.all_infos = self._get_all_infos()
        self.details = None
        self.episode_infos = None

    
    def _get_all_infos(self):
        sql = f"""
        SELECT *
        FROM podcasts
        WHERE id = {self.id}
        """
        return self.db_connector.query(sql)
    
    def get_info(self, column_name):
        return self.all_infos[column_name][0]
    

    def get_details(self):
        if not self.details:
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
                , ', ') as categories
            FROM podcasts
            WHERE id = {self.id}
            """
            self.details = self.db_connector.query(sql)
        return self.details
    

    @staticmethod
    def _parse_date(date_str):
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


    def get_episode_infos(self):
        if not self.episode_infos:
            url = self.get_info("url")
            feed = fp.parse(url)
            df = pl.DataFrame(
                {
                    "title": [entry["title"] for entry in feed["entries"]],
                    "date": [self._parse_date(entry["published"]) for entry in feed["entries"]],
                    "duration": [entry["itunes_duration"] for entry in feed["entries"]],
                }
            )
            self.episode_infos = df
        return self.episode_infos
