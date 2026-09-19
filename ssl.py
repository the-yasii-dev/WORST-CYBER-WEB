from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import ssl
import socket
from datetime import datetime

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
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(10)
                s.connect((domain, 443))
                cert = s.getpeercert()
                
                exp = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                days_left = (exp - datetime.now()).days
                
                issuer_dict = dict(x[0] for x in cert['issuer'])
                
                result = {
                    "domain": domain,
                    "valid": True,
                    "expires": cert['notAfter'],
                    "days_left": days_left,
                    "issuer": issuer_dict.get('organizationName', 'Unknown')
                }
        except Exception as e:
            result = {"domain": domain, "valid": False, "error": str(e)}
        
        self.wfile.write(json.dumps(result).encode())