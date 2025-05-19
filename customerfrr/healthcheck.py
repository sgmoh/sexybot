import os
import http.server
import socketserver
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('healthcheck')

PORT = int(os.getenv("PORT", "8080"))

class HealthcheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for UptimeRobot healthcheck"""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Bot is running')
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

def start_healthcheck_server():
    """Start the healthcheck server in a separate thread"""
    try:
        handler = HealthcheckHandler
        httpd = socketserver.TCPServer(("", PORT), handler)
        logger.info(f"Starting healthcheck server on port {PORT}")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting healthcheck server: {e}")

def run_healthcheck():
    """Run the healthcheck server in a separate thread"""
    thread = threading.Thread(target=start_healthcheck_server)
    thread.daemon = True
    thread.start()
    return thread

if __name__ == "__main__":
    run_healthcheck()
    logger.info("Healthcheck server started")
    
    # Keep the script running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Shutting down...")