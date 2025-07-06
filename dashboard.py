from http.server import HTTPServer, BaseHTTPRequestHandler
from redis_db import get_priority_links, get_all_products
from redis.exceptions import ConnectionError as RedisConnectionError
import json
import time

class DashboardHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        if self.path == '/api/priority':
            try:
                links = get_priority_links()
            except RedisConnectionError:
                self._send_json({'error': 'Cannot connect to Redis'}, status=503)
                return
            self._send_json(links)
            return
        elif self.path == '/api/products':
            try:
                products = get_all_products()
            except RedisConnectionError:
                self._send_json({'error': 'Cannot connect to Redis'}, status=503)
                return
            self._send_json(products)
            return

        try:
            priority = get_priority_links()
        except RedisConnectionError:
            html = (
                "<html><body><h1>Service Unavailable</h1>"
                "<p>Cannot connect to Redis</p></body></html>"
            )
            self._send_html(html, status=503)
            return
        html = ["<html><head>",
                "<meta http-equiv='refresh' content='10'>",
                "<title>LaBotBot Status</title>",
                "</head><body>",
                "<h1>LaBotBot Status</h1>",
                f"<p>Updated: {time.ctime()}</p>",
                "<h2>Priority Links</h2>",
                "<ul>"]
        for link in priority:
            html.append(f"<li>{link}</li>")
        html.extend(["</ul>", "</body></html>"])
        html_content = "".join(html)
        self._send_html(html_content)

def run(port=8000):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"Serving dashboard on http://0.0.0.0:{port} ...")
    server.serve_forever()

if __name__ == '__main__':
    run()
