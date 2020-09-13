import sys
from http.server import test, SimpleHTTPRequestHandler


class CorsRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    extensions_map = {
        k: v + (';charset=UTF-8' if v.startswith('text/') else '')
        for k, v in SimpleHTTPRequestHandler.extensions_map.items()
    }


test(CorsRequestHandler, port=int(sys.argv[1]))
