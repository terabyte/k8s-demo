#!/usr/bin/env python2

# cribbed partially from https://www.acmesystems.it/python_http
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import sys
import string


if __name__ == '__main__':

    port = 8080
    if len(sys.argv) > 1:
        port = string.atoi(sys.argv[1])

    class hwHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write("Hello, World!\n")
            return

    # create web server and define handler to manage incoming requests
    server = HTTPServer(('', port), hwHandler)
    print('Started http server on port ', port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down http server on port ', port)
        server.shutdown()
        sys.exit(0)
