import sys
import time
from http.server import test, SimpleHTTPRequestHandler


class CorsRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def log_message(self, format, *args):
        timestamp = time.strftime("%H:%M:%S")
        sys.stderr.write(f"{timestamp} {format % args}\n")

    extensions_map = {
        k: v + (';charset=UTF-8' if v.startswith('text/') else '')
        for k, v in SimpleHTTPRequestHandler.extensions_map.items()
    }


test(CorsRequestHandler, port=int(sys.argv[1]))
