#!/usr/bin/env python2

# cribbed partially from https://www.acmesystems.it/python_http
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import string
import sys
import threading


if __name__ == '__main__':

    # https://stackoverflow.com/a/8934902/156785
    atomic_int = [1]
    atomic_int_lock = threading.Lock()

    port = 8080
    if len(sys.argv) == 2:
        port = string.atoi(sys.argv[1])
    elif len(sys.argv) != 1:
        print("Usage: Must provide zero or one argument [port]")
        print("    Default: port => 8080")
        sys.exit(1)

    class hwHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            atomic_int_lock.acquire()
            value = atomic_int[0]
            atomic_int[0] = atomic_int[0] + 1
            atomic_int_lock.release()

            self.wfile.write("{\"data\":%s}" % value)
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
