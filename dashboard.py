from http.server import HTTPServer, BaseHTTPRequestHandler
from redis_db import get_priority_links, get_all_products
import json
import time
import os
import argparse
import html

class DashboardHandler(BaseHTTPRequestHandler):
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        if self.path == '/api/priority':
            links = get_priority_links()
            self._send_json(links)
            return
        elif self.path == '/api/products':
            products = get_all_products()
            self._send_json(products)
            return

        priority = get_priority_links()
        html_parts = ["<html><head>",
                "<meta http-equiv='refresh' content='10'>",
                "<title>LaBotBot Status</title>",
                "</head><body>",
                "<h1>LaBotBot Status</h1>",
                f"<p>Updated: {time.ctime()}</p>",
                "<h2>Priority Links</h2>",
                "<ul>"]
        for link in priority:
            html_parts.append(f"<li>{html.escape(link)}</li>")
        html_parts.extend(["</ul>", "</body></html>"])
        html_content = "".join(html_parts)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

def run(host=None, port=None):
    if host is None:
        host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    if port is None:
        port = int(os.getenv("DASHBOARD_PORT", "8000"))

    server = HTTPServer((host, port), DashboardHandler)
    print(f"Serving dashboard on http://{host}:{port} ...")
    server.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Start the LaBotBot dashboard")
    parser.add_argument("--host", help="Interface to bind to", default=os.getenv("DASHBOARD_HOST"))
    parser.add_argument("--port", type=int, help="Port to listen on", default=os.getenv("DASHBOARD_PORT"))
    args = parser.parse_args()
    run(args.host, args.port)
