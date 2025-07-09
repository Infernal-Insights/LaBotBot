from http.server import HTTPServer, BaseHTTPRequestHandler
from labot.redis_db import get_priority_links, get_all_products
from labot.sync_to_mongo import sync_from_mongo_to_redis
import subprocess
import json
import time
import html
import base64
import os

DASHBOARD_USER = os.getenv("DASHBOARD_USER")
DASHBOARD_PASS = os.getenv("DASHBOARD_PASS")


def fetch_products():
    """Return products from Redis or fall back to MongoDB."""
    products = get_all_products()
    if not products:
        try:
            sync_from_mongo_to_redis(limit=50)
            products = get_all_products()
        except Exception as e:
            print(f"Mongo fallback failed: {e}")
    # Filter out items that have both a blank name and blank price
    def is_blank(value: str) -> bool:
        return value is None or str(value).strip() == ""

    filtered = []
    for p in products:
        if hasattr(p, "get"):
            if is_blank(p.get("name")) and is_blank(p.get("price")):
                continue
        filtered.append(p)
    products = filtered
    return products


def read_buyer_logs(lines=20):
    """Return the last N lines of the buyer bot log."""
    log_path = "buyer_bot.log"
    if not os.path.exists(log_path):
        return "buyer_bot.log not found"
    try:
        with open(log_path, "r") as f:
            return "".join(f.readlines()[-lines:])
    except Exception as e:
        return f"Error reading log: {e}"


def is_process_running(pattern: str) -> bool:
    """Check if a process with the given pattern is running."""
    try:
        subprocess.run(["pgrep", "-f", pattern], check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


class DashboardHandler(BaseHTTPRequestHandler):
    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _check_auth(self):
        """Return True if auth disabled or Authorization header is valid."""
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
            products = fetch_products()
            self._send_json(products)
            return
        elif self.path == '/api/logs':
            self._send_json({'logs': read_buyer_logs()})
            return

        priority = get_priority_links()
        products = fetch_products()
        logs = read_buyer_logs()
        status = {
            "buyer_bot": "Running" if is_process_running("buyer_bot.py") else "Stopped",
            "scraper": "Running" if is_process_running("scraper.py") else "Stopped",
        }

        product_rows = "".join(
            f"<tr><td>{html.escape(p.get('name', ''))}</td>"
            f"<td>${p.get('price', '')}</td>"
            f"<td>{'Yes' if p.get('in_stock') == '1' else 'No'}</td></tr>"
            for p in products
        )
        priority_items = "".join(f"<li>{html.escape(l)}</li>" for l in priority)

        html_content = f"""
        <html>
        <head>
            <meta http-equiv='refresh' content='30'>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            <title>LaBotBot Status</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, sans-serif;
                    background: linear-gradient(135deg, #f0f4f7, #d9e2ec);
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    max-width: 900px;
                    margin: auto;
                    background: #fff;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    padding: 20px;
                }}
                nav {{
                    margin: 20px 0;
                    text-align: center;
                }}
                nav a {{
                    margin: 0 10px;
                    padding: 10px 15px;
                    text-decoration: none;
                    border-radius: 4px;
                    background: #3498db;
                    color: #fff;
                    transition: background .3s;
                    cursor: pointer;
                }}
                nav a:hover, nav a.active {{
                    background: #2980b9;
                }}
                section {{ display: none; }}
                section.active {{ display: block; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:nth-child(even) {{ background: #f9f9f9; }}
                ul {{ list-style: none; padding: 0; }}
                ul li {{
                    padding: 8px 10px;
                    margin: 5px 0;
                    background: #ecf0f1;
                    border-radius: 4px;
                }}
                .status ul li {{
                    background: none;
                    padding: 4px 0;
                }}
                pre {{
                    background: #2d2d2d;
                    color: #f8f8f2;
                    padding: 15px;
                    border-radius: 4px;
                    max-height: 400px;
                    overflow: auto;
                }}
            </style>
            <script>
                function show(tab) {{
                    document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
                    document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
                    document.getElementById(tab).classList.add('active');
                    const link = document.querySelector(`nav a[data-tab="${{tab}}"]`);
                    if (link) link.classList.add('active');
                }}
                window.onload = () => show('products');
            </script>
        </head>
        <body>
        <div class='container'>
            <h1>LaBotBot Status</h1>
            <p>Updated: {time.ctime()}</p>
            <nav>
                <a data-tab='products' onclick=\"show('products')\">Products</a>
                <a data-tab='logs' onclick=\"show('logs')\">Logs</a>
            </nav>
            <section id='products' class='active'>
                <h2>Priority Links</h2>
                <ul>{priority_items}</ul>
                <h2>Products</h2>
                <table>
                    <tr><th>Name</th><th>Price</th><th>In Stock</th></tr>
                    {product_rows}
                </table>
            </section>
            <section id='logs'>
                <pre>{html.escape(logs)}</pre>
            </section>
            <div class='status'>
                <h2>Service Status</h2>
                <ul>
                    <li>Buyer Bot: {status['buyer_bot']}</li>
                    <li>Scraper: {status['scraper']}</li>
                </ul>
            </div>
        </div>
        </body>
        </html>
        """
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
