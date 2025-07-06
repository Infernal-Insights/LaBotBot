from http.server import HTTPServer, BaseHTTPRequestHandler
from redis_db import get_priority_links, get_all_products
import json
import time
import html
import base64
import os

DASHBOARD_USER = os.getenv("DASHBOARD_USER")
DASHBOARD_PASS = os.getenv("DASHBOARD_PASS")


class DashboardHandler(BaseHTTPRequestHandler):
    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _check_auth(self):
        """Return True if auth disabled or Authorization header is valid."""
        """Return True if no auth required or valid Basic Auth header present."""
        if not DASHBOARD_USER:
            return True
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(auth_header.split(" ")[1]).decode()
            user, _, password = decoded.partition(":")
        except Exception:
            return False
        return user == DASHBOARD_USER and password == DASHBOARD_PASS

    def do_GET(self):
        if not self._check_auth():
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\"LaBotBot\"")
            self.end_headers()
            return
        if self.path == '/api/priority':
            links = get_priority_links()
            self._send_json(links)
            return
        elif self.path == '/api/products':
            products = get_all_products()
            self._send_json(products)
            return

        priority = get_priority_links()
        products = get_all_products()

        html_parts = [
            "<html><head>",
            "<meta http-equiv='refresh' content='10'>",
            "<title>LaBotBot Status</title>",
            "</head><body>",
            "<h1>LaBotBot Status</h1>",
            f"<p>Updated: {time.ctime()}</p>",
            "<h2>Priority Links</h2>",
            "<ul>"
        ]
        for link in priority:
            html_parts.append(f"<li>{html.escape(link)}</li>")
        html_parts.extend([
            "</ul>",
            "<h2>Products</h2>",

            (
                "<table border='1'><tr>"
                "<th>Name</th><th>Price</th><th>In Stock</th></tr>"
            )
            "<table border='1'><tr><th>Name</th><th>Price</th><th>In Stock</th></tr>"

        ])
        for p in products:
            name = html.escape(p.get("name", ""))
            price = p.get("price", "")
            stock = "Yes" if p.get("in_stock") == '1' else "No"
            html_parts.append(
                f"<tr><td>{name}</td><td>${price}</td><td>{stock}</td></tr>"
            )
        html_parts.extend(["</table>", "</body></html>"])
        html_content = "".join(html_parts)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())



def run(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), DashboardHandler)
    print(f"Serving dashboard on http://{host}:{port} ...")
    server.serve_forever()


if __name__ == '__main__':

    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("DASHBOARD_PORT", "8000"))
    run(host=host, port=port)
