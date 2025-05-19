import os
import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bot_launcher')

# Add the customerfrr directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'customerfrr'))

# Import the necessary functions from the bot module
from customerfrr.bot import initialize_bot

async def main():
    """Initialize and start the Discord bot"""
    try:
        # Initialize the bot
        bot = initialize_bot()
        
        # Get the token from environment variables
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.critical("No Discord token found in environment variables!")
            return
        
        # Start the bot
        logger.info("Starting Discord bot...")
        await bot.start(token)
    except Exception as e:
        logger.critical(f"Error starting bot: {e}")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())