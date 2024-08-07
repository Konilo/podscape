import logging
from datetime import datetime
import re
import urllib.request as urlreq
from urllib.error import URLError

import polars as pl
import feedparser as fp


COVER_PLACEHOLDER_PATH = "podscape/www/cover_placeholder.png"

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
        if column_name == "categories":
            # join categories 1 to 10
            return ", ".join([
                self.all_infos[f"category{i}"][0] for i in range(1, 11) if self.all_infos[f"category{i}"][0]
            ])

        elif column_name == "imageUrl":
            cover_url = self.all_infos[column_name][0]
            if not cover_url or cover_url == "":
                return COVER_PLACEHOLDER_PATH
            try:
                code = urlreq.urlopen(cover_url).getcode()
            except URLError:
                return COVER_PLACEHOLDER_PATH
            if code != 200:
                return COVER_PLACEHOLDER_PATH
            else:
                return cover_url

        else:
            return self.all_infos[column_name][0]
    

    @staticmethod
    def _parse_date(date_str):
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return f"{date_str} (parsing error)"


    @staticmethod
    def _format_duration(duration):
        if isinstance(duration, str):
            if re.match(r"^\d+$", duration):
                return round(int(duration)/60)
            elif re.match(r"^\d{2}:\d{2}:\d{2}$", duration):
                return round(int(duration.split(":")[0])*60 + int(duration.split(":")[1]) + int(duration.split(":")[2])/60)
        return f"{duration} (parsing error)"


    def get_episode_infos(self):
        if not self.episode_infos:
            url = self.get_info("url")
            feed = fp.parse(url)
            df = pl.DataFrame(
                {
                    "#": range(len(feed["entries"]), 0, -1),
                    "title": [entry["title"] for entry in feed["entries"]],
                    "date": [self._parse_date(entry["published"]) for entry in feed["entries"]],
                    "duration": [self._format_duration(entry["itunes_duration"]) for entry in feed["entries"]],
                }
            )
            self.episode_infos = df
        return self.episode_infos
