import sqlite3
import polars as pl
import logging
import os


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SqliteConnector:
    """A class to simplify operations on a SQLite3 database"""

    def __init__(self, db_file_path: str):
        self.db_file_path = db_file_path
        self.con = None

    def connect(self):
        if not self.con:
            logger.info("Establishing connection to the DB")
            if not os.path.exists(self.db_file_path):
                raise FileNotFoundError(f"Database file not found: {self.db_file_path}")
            self.con = sqlite3.connect(self.db_file_path)

    def close(self):
        if self.con:
            self.con.close()
            self.con = None
            logger.info("Connection to the DB closed")

    def query(self, query: str, output_class: str = "polars"):
        self.connect()
        logger.info(f"Executing query")
        cursor = self.con.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        self.close()
        logger.info(f"Query executed successfully")

        if output_class == "polars":
            return pl.DataFrame(rows, schema=column_names)
        else:
            raise ValueError(f"Unsupported output class: {output_class}")
