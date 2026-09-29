import os

import psycopg2

from utils.logger import get_logger


logger = get_logger(__name__)


def get_connection():
    """
    Create and return a connection to the PostgreSQL database.
    """

    logger.info("Connecting to PostgreSQL database")

    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "course_platform"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )

    logger.info("PostgreSQL database connection established")

    return connection