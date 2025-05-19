import os
import time
import http.server
import socketserver
import threading
import logging
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('uptime_monitor')

# Default to port 8080 if not specified in environment
PORT = int(os.getenv("PORT", "8080"))

# Store bot status information
bot_status = {
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

def update_stats(guilds=None, users=None, commands=None):
    """Update the bot statistics"""
    global bot_status
    
    if guilds is not None:
        bot_status["stats"]["guilds"] = guilds
    
    if users is not None:
        bot_status["stats"]["users"] = users
    
    if commands is not None:
        bot_status["stats"]["commands_processed"] = commands
    
    # Update the uptime
    start_time = datetime.fromisoformat(bot_status["started_at"])
    now = datetime.now()
    bot_status["uptime_seconds"] = (now - start_time).total_seconds()
    bot_status["last_checked"] = now.isoformat()

class UptimeMonitorHandler(http.server.SimpleHTTPRequestHandler):
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
            self.wfile.write(json.dumps(bot_status).encode())
        elif self.path == '/dashboard':
            # Return HTML dashboard
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            uptime_str = f"{int(bot_status['uptime_seconds'] // 3600)}h {int((bot_status['uptime_seconds'] % 3600) // 60)}m {int(bot_status['uptime_seconds'] % 60)}s"
            
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
                        <h3><span class="status {'online' if bot_status['healthy'] else 'offline'}"></span> Status: {'Online' if bot_status['healthy'] else 'Offline'}</h3>
                        <p>Started: {bot_status['started_at']}</p>
                        <p>Uptime: {uptime_str}</p>
                        <p>Last checked: {bot_status['last_checked']}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Statistics</h3>
                        <p>Servers: {bot_status['stats']['guilds']}</p>
                        <p>Users: {bot_status['stats']['users']}</p>
                        <p>Commands processed: {bot_status['stats']['commands_processed']}</p>
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

def start_uptime_monitor():
    """Start the UptimeRobot monitor server in a separate thread"""
    try:
        handler = UptimeMonitorHandler
        # Allow reuse of the address in case it's already in use
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("0.0.0.0", PORT), handler)
        logger.info(f"Starting UptimeRobot monitor server on port {PORT}")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting UptimeRobot monitor server: {e}")

def run_uptime_monitor():
    """Run the UptimeRobot monitor server in a separate thread"""
    thread = threading.Thread(target=start_uptime_monitor)
    thread.daemon = True
    thread.start()
    logger.info(f"UptimeRobot monitor started on port {PORT}")
    return thread

# Update stats in a background thread
def stats_updater():
    """Background thread to regularly update bot stats and uptime"""
    while True:
        update_stats()
        time.sleep(30)  # Update every 30 seconds

def start_stats_updater():
    """Start the stats updater in a background thread"""
    thread = threading.Thread(target=stats_updater)
    thread.daemon = True
    thread.start()
    return thread

if __name__ == "__main__":
    # Test the monitor by itself
    run_uptime_monitor()
    start_stats_updater()
    
    # Keep the script running for testing
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")