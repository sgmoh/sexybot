import os
import asyncio
import logging
from dotenv import load_dotenv
from discord_bot import bot
from healthcheck import run_healthcheck
import models  # Import to initialize the database

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('bot_main')

# Load environment variables
load_dotenv()

# Start the healthcheck server for UptimeRobot
healthcheck_thread = run_healthcheck()
logger.info("Healthcheck server started for UptimeRobot monitoring")

async def main():
    """Main function to start the bot"""
    try:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            logger.critical("No Discord token found in environment variables!")
            return
        
        # Log information about the database
        db_url = os.getenv("DATABASE_URL", "JSON database (no PostgreSQL)")
        if "postgresql" in db_url:
            masked_url = db_url.replace("://", "://****:****@")
            logger.info(f"Using PostgreSQL database: {masked_url}")
        else:
            logger.info("Using JSON database as fallback")
        
        logger.info("Starting Discord bot...")
        await bot.start(token)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())