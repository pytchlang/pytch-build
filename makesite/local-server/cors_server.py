import sys
import time
from http import HTTPStatus
from http.server import test, SimpleHTTPRequestHandler


class CorsRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def log_request(self, code="-", size="-"):
        if isinstance(code, HTTPStatus):
            code = code.value
        if self.command is None:
            # Request line could not be parsed; show it as received.
            self.log_message("%r %s", self.requestline, code)
        else:
            self.log_message("%s %s %s", self.command, self.path, code)

    def log_message(self, format, *args):
        timestamp = time.strftime("%H:%M:%S")
        sys.stderr.write(f"{timestamp} {format % args}\n")

    extensions_map = {
        k: v + (';charset=UTF-8' if v.startswith('text/') else '')
        for k, v in SimpleHTTPRequestHandler.extensions_map.items()
    }


test(CorsRequestHandler, port=int(sys.argv[1]))
