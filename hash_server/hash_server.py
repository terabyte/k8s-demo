#!/usr/bin/env python2

# cribbed partially from https://www.acmesystems.it/python_http
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import hashlib
import httplib
import json
import string
import sys


if __name__ == '__main__':

    self_port = 8080
    persistence_server = 'localhost:8081'

    if len(sys.argv) == 3:
        self_port = string.atoi(sys.argv[1])
        persistence_server = sys.argv[2]
    elif len(sys.argv) != 1:
        print("Usage: Must provide zero or two arguments [self_port, persistence_server]")
        print("    Defaults: self_port => 8081, persistence_server => localhost:8081")
        sys.exit(1)

    class hwHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_header('Content-Type', 'application/json')

            # get value from persistence service
            conn = httplib.HTTPConnection(persistence_server)
            conn.request("GET", "/")
            res = conn.getresponse()
            if res.status != 200:
                self.send_response(500)
                self.end_headers()
                self.wfile.write("{\"error\":\"Persistence Store Error: %s: %s\"}" % (res.status, res.reason))
                return

            self.send_response(200)
            self.end_headers()

            value_str = res.read()
            value = json.loads(value_str)["data"]

            # hash it
            m = hashlib.sha256()
            m.update(str(value))
            value_hashed = m.hexdigest()

            self.wfile.write("{\"data\":{\"number\":%s,\"hash\":\"%s\"}}" % (value, value_hashed))
            return

    # create web server and define handler to manage incoming requests
    server = HTTPServer(('', self_port), hwHandler)
    print('Started http server on port ', self_port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down http server on port ', self_port)
        server.shutdown()
        sys.exit(0)
