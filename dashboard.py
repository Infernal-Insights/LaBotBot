from http.server import HTTPServer, BaseHTTPRequestHandler
from redis_db import get_priority_links, get_all_products
import json
import time

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
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

def run(port=8000):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"Serving dashboard on http://0.0.0.0:{port} ...")
    server.serve_forever()

if __name__ == '__main__':
    run()
