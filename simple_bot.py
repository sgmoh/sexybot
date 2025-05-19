import os
import discord
import asyncio
import logging
import http.server
import socketserver
import threading
import json
import time
from datetime import datetime
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('discord_bot')

# Load environment variables
load_dotenv()

# Discord bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '!'

# UptimeRobot configuration
PORT = int(os.getenv("PORT", "8080"))

# Bot statistics for UptimeRobot
bot_stats = {
    "started_at": datetime.now().isoformat(),
    "uptime_seconds": 0,
    "last_checked": datetime.now().isoformat(),
    "healthy": True,
    "stats": {
        "guilds": 0,
        "users": 0,
        "commands_processed": 0
    }
}

# UptimeRobot HTTP server handler
class UptimeRobotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for UptimeRobot healthcheck"""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Bot is running')
        elif self.path == '/status':
            # Return detailed JSON status
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(bot_stats).encode())
        elif self.path == '/dashboard':
            # Return HTML dashboard
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            uptime_str = f"{int(bot_stats['uptime_seconds'] // 3600)}h {int((bot_stats['uptime_seconds'] % 3600) // 60)}m {int(bot_stats['uptime_seconds'] % 60)}s"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Discord Bot Status</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    h1 {{ color: #5865F2; }}
                    .stat-box {{ background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 4px; }}
                    .status {{ display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px; }}
                    .status.online {{ background-color: #43B581; }}
                    .status.offline {{ background-color: #F04747; }}
                    .refresh {{ color: #5865F2; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Discord Bot Status Dashboard</h1>
                    <div class="stat-box">
                        <h3><span class="status {'online' if bot_stats['healthy'] else 'offline'}"></span> Status: {'Online' if bot_stats['healthy'] else 'Offline'}</h3>
                        <p>Started: {bot_stats['started_at']}</p>
                        <p>Uptime: {uptime_str}</p>
                        <p>Last checked: {bot_stats['last_checked']}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Statistics</h3>
                        <p>Servers: {bot_stats['stats']['guilds']}</p>
                        <p>Users: {bot_stats['stats']['users']}</p>
                        <p>Commands processed: {bot_stats['stats']['commands_processed']}</p>
                    </div>
                    <p><a class="refresh" onclick="location.reload()">Refresh</a></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - - [%s] %s" %
                    (self.client_address[0],
                     self.log_date_time_string(),
                     format % args))

# Start UptimeRobot HTTP server
def start_uptime_monitor():
    """Start the UptimeRobot monitor server in a separate thread"""
    try:
        handler = UptimeRobotHandler
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("0.0.0.0", PORT), handler)
        logger.info(f"Starting UptimeRobot monitor server on port {PORT}")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting UptimeRobot monitor server: {e}")

# Run UptimeRobot monitor
def run_uptime_monitor():
    """Run the UptimeRobot monitor server in a separate thread"""
    thread = threading.Thread(target=start_uptime_monitor)
    thread.daemon = True
    thread.start()
    logger.info(f"UptimeRobot monitor started on port {PORT}")
    return thread

# Update stats in a background thread
def update_stats_task():
    """Background thread to regularly update bot stats and uptime"""
    global bot_stats
    while True:
        # Update the uptime
        start_time = datetime.fromisoformat(bot_stats["started_at"])
        now = datetime.now()
        bot_stats["uptime_seconds"] = (now - start_time).total_seconds()
        bot_stats["last_checked"] = now.isoformat()
        time.sleep(30)  # Update every 30 seconds

# Start the stats updater
def start_stats_updater():
    """Start the stats updater in a background thread"""
    thread = threading.Thread(target=update_stats_task)
    thread.daemon = True
    thread.start()
    return thread

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Track command execution count
command_count = 0

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    global bot_stats
    
    logger.info(f'Bot logged in as {bot.user.name} (ID: {bot.user.id})')
    
    # Update UptimeRobot stats with guild and user information
    total_users = sum(guild.member_count for guild in bot.guilds)
    bot_stats["stats"]["guilds"] = len(bot.guilds)
    bot_stats["stats"]["users"] = total_users
    
    logger.info(f'Bot is in {len(bot.guilds)} guilds with {total_users} total users')
    
    # Start the stats update task
    update_stats.start()
    
    # Set bot status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"{PREFIX}help"
    ))

@bot.event
async def on_command_completion(ctx):
    """Track command usage for UptimeRobot stats"""
    global command_count, bot_stats
    command_count += 1
    bot_stats["stats"]["commands_processed"] = command_count
    logger.info(f"Command processed: {ctx.command.name} (Total: {command_count})")

@bot.event
async def on_guild_join(guild):
    """Update stats when bot joins a new guild"""
    global bot_stats
    bot_stats["stats"]["guilds"] = len(bot.guilds)
    total_users = sum(g.member_count for g in bot.guilds)
    bot_stats["stats"]["users"] = total_users
    logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_guild_remove(guild):
    """Update stats when bot leaves a guild"""
    global bot_stats
    bot_stats["stats"]["guilds"] = len(bot.guilds)
    total_users = sum(g.member_count for g in bot.guilds)
    bot_stats["stats"]["users"] = total_users
    logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

@tasks.loop(minutes=5)
async def update_stats():
    """Update bot stats periodically"""
    global bot_stats
    total_users = sum(guild.member_count for guild in bot.guilds)
    bot_stats["stats"]["guilds"] = len(bot.guilds)
    bot_stats["stats"]["users"] = total_users
    logger.info(f"Stats updated: {len(bot.guilds)} guilds, {total_users} users, {command_count} commands")

# Basic bot commands
@bot.command(name="ping", help="Check the bot's latency")
async def ping(ctx):
    """Simple ping command to check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency}ms")

@bot.command(name="uptime", help="Check the bot's uptime")
async def uptime(ctx):
    """Show the bot's uptime"""
    uptime_seconds = bot_stats["uptime_seconds"]
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    await ctx.send(f"⏱️ Bot has been online for: {hours}h {minutes}m {seconds}s")

@bot.command(name="stats", help="Show bot statistics")
async def stats(ctx):
    """Show the bot statistics"""
    embed = discord.Embed(
        title="📊 Bot Statistics",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Servers", value=str(bot_stats["stats"]["guilds"]), inline=True)
    embed.add_field(name="Users", value=str(bot_stats["stats"]["users"]), inline=True)
    embed.add_field(name="Commands Used", value=str(bot_stats["stats"]["commands_processed"]), inline=True)
    
    uptime_seconds = bot_stats["uptime_seconds"]
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    embed.add_field(name="Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=False)
    
    embed.add_field(name="Status Dashboard", value=f"[View Dashboard](http://{os.getenv('REPL_SLUG', 'localhost')}:{PORT}/dashboard)", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="status", help="Check the bot's status")
async def status(ctx):
    """Show the bot's status"""
    embed = discord.Embed(
        title="✅ Bot Status",
        description="The bot is running properly!",
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)

# Main function to start the bot
async def start_bot():
    """Start the Discord bot"""
    try:
        logger.info("Starting Discord bot...")
        await bot.start(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")

# Run the bot
if __name__ == "__main__":
    # Start UptimeRobot monitor
    monitor_thread = run_uptime_monitor()
    
    # Start stats updater
    stats_thread = start_stats_updater()
    
    # Run the bot
    asyncio.run(start_bot())