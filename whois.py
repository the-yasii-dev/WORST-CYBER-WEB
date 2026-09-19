from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import socket

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        domain = query.get('domain', [''])[0]
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not domain:
            self.wfile.write(json.dumps({"error": "domain required"}).encode())
            return
        
        try:
            ip = socket.gethostbyname(domain)
            result = {
                "domain": domain,
                "ip": ip,
                "status": "active"
            }
        except:
            result = {"domain": domain, "ip": "N/A", "status": "not found"}
        
        self.wfile.write(json.dumps(result).encode())