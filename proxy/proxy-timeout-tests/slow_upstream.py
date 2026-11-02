#!/usr/bin/env python3
"""A test upstream that answers slowly, to reproduce proxy timeouts.

For every request it reads the whole request body, waits, then replies with a small JSON body.
The wait is the number in a `/delay/<seconds>/` path segment, or --default-delay when the
path has none. No response headers are sent during the wait, so the caller sees a stalled
upstream, not a slow download.

    python slow_upstream.py --default-delay 90 --port 9500

Expose the port through a public https tunnel (for example `ngrok http 9500`) and point a
test connection at the tunnel URL. See README.md. Stop the server and the tunnel when you
finish: the tunnel is a public URL that reaches this machine.
"""
import argparse
import datetime
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-3] + "Z"


class StalledServer(ThreadingHTTPServer):
    # The default listen backlog is 5. Several stalled requests can arrive at once, and a refused
    # connection shows up in the caller as a 502 from the tunnel, not as a stalled upstream.
    request_queue_size = 128
    daemon_threads = True


def make_handler(default_delay: int):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def handle_any(self):
            length = int(self.headers.get("Content-Length") or 0)
            print(f"[{stamp()}] {self.command} {self.path[:90]} content-length={length}", file=sys.stderr, flush=True)
            received = 0
            while received < length:
                chunk = self.rfile.read(min(65536, length - received))
                if not chunk:
                    break
                received += len(chunk)
            match = re.search(r"/delay/(\d+)", self.path)
            delay = int(match.group(1)) if match else default_delay
            print(f"[{stamp()}] body read ({received} bytes); waiting {delay}s with no response", file=sys.stderr, flush=True)
            time.sleep(delay)
            payload = b'{"slow":"ok"}'
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except OSError:
                pass  # the caller or the load balancer gave up first

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = handle_any

        def log_message(self, *_):
            return

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=9500)
    parser.add_argument("--default-delay", type=int, default=90, help="seconds to wait when the path has no /delay/<n>/ segment")
    args = parser.parse_args()
    server = StalledServer(("127.0.0.1", args.port), make_handler(args.default_delay))
    print(f"listening on 127.0.0.1:{args.port}, default delay {args.default_delay}s", file=sys.stderr, flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
