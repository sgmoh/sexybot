import os
import discord
import asyncio
import logging
from discord.ext import commands
from config import CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('discord_bot')

# Discord Intents configuration
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
intents.guilds = True
intents.invites = True
intents.reactions = True

# Initialize the bot
bot = commands.Bot(command_prefix=CONFIG['prefix'], intents=intents, help_command=None)

# Event: Bot is ready
@bot.event
async def on_ready():
    logger.info(f'Bot logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Running with prefix: {CONFIG["prefix"]}')
    
    # Load all cogs
    for extension in CONFIG['cogs']:
        try:
            await bot.load_extension(f'cogs.{extension}')
            logger.info(f'Loaded extension: {extension}')
        except Exception as e:
            logger.error(f'Failed to load extension {extension}: {e}')
    
    # Set the bot's status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"for {CONFIG['prefix']}help"
    ))
    
    # Update UptimeRobot monitor stats
    try:
        from uptime_monitor import update_stats
        total_users = sum(guild.member_count for guild in bot.guilds)
        update_stats(
            guilds=len(bot.guilds),
            users=total_users
        )
        logger.info(f'Updated UptimeRobot stats: {len(bot.guilds)} guilds, {total_users} users')
    except ImportError:
        logger.warning('UptimeRobot monitor module not found, stats not updated')
    except Exception as e:
        logger.error(f'Failed to update UptimeRobot stats: {e}')
    
    logger.info('Bot is ready!')

# Track command execution count for UptimeRobot stats
command_count = 0

@bot.event
async def on_command_completion(ctx):
    global command_count
    command_count += 1
    
    # Update UptimeRobot monitor stats for commands
    try:
        from uptime_monitor import update_stats
        update_stats(commands=command_count)
    except ImportError:
        pass
    except Exception as e:
        logger.error(f'Failed to update UptimeRobot command stats: {e}')

# Event: Handle command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}. Use `{CONFIG['prefix']}help` for command usage.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"❌ I need the following permissions to run this command: {', '.join(error.missing_permissions)}")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        logger.error(f'Command error: {error}')

# Run the bot
async def main():
    try:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            logger.critical("No Discord token found in environment variables!")
            return
        
        await bot.start(token)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())