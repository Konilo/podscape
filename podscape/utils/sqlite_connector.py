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

    def query(self, sql: str, output_class: str = "polars", infer_date_cols: bool = True):
        self.connect()
        logger.info(f"Querying the DB")
        cursor = self.con.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        logger.info(f"Querying completed")
        self.close()

        if output_class == "polars":
            df = pl.DataFrame(rows, schema=column_names)
            if infer_date_cols:
                date_substrings = ["date", "day", "week", "month", "semester", "year"]
                for col_name in column_names:
                    if any(substring in col_name.lower() for substring in date_substrings):
                        df = df.with_columns(pl.col(col_name).cast(pl.Date))
            return df
        elif output_class == "list":
            if len(column_names) == 1:
                return [row[0] for row in rows]
            else:
                raise ValueError("Output class 'list' is only supported for single-column queries")
        else:
            raise ValueError(f"Unsupported output class: {output_class}")
