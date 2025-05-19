import os
import logging
from utils.database import db as json_db
from utils.db_postgres import db as postgres_db

# Set up logging
logger = logging.getLogger('discord_bot')

# Determine which database to use based on environment variable
USE_POSTGRES = os.getenv("USE_POSTGRES", "true").lower() in ("true", "1", "yes")

# Set the active database
if USE_POSTGRES:
    logger.info("Using PostgreSQL database")
    db = postgres_db
else:
    logger.info("Using JSON database")
    db = json_db