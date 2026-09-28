#!/usr/bin/env python3
# Minimal HTTP CONNECT proxy: Basic auth (user:pass in argv[2],
# empty = open), 407 on a bad credential, 200 + a byte pump on a
# good one. Enough to prove the role tunnels correctly.
import base64, socket, socketserver, sys, threading
port, auth = int(sys.argv[1]), sys.argv[2]
want = 'Basic ' + base64.b64encode(auth.encode()).decode() if auth else None

def pump(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

class Tunnel(socketserver.BaseRequestHandler):
    def handle(self):
        raw = b''
        while b'\r\n\r\n' not in raw:
            chunk = self.request.recv(4096)
            if not chunk:
                return
            raw += chunk
        lines = raw.split(b'\r\n\r\n', 1)[0].decode(errors='replace').split('\r\n')
        method, target = lines[0].split()[:2]
        headers = {k.strip().lower(): v.strip()
                   for k, v in (h.split(':', 1) for h in lines[1:] if ':' in h)}
        if method != 'CONNECT':
            self.request.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
            return
        if want and headers.get('proxy-authorization') != want:
            self.request.sendall(b'HTTP/1.1 407 Proxy Authentication Required\r\n'
                                 b'Proxy-Authenticate: Basic realm="sleuth"\r\n\r\n')
            return
        host, _, tport = target.rpartition(':')
        try:
            upstream = socket.create_connection((host, int(tport)), timeout=10)
        except OSError:
            self.request.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            return
        self.request.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
        t = threading.Thread(target=pump, args=(upstream, self.request), daemon=True)
        t.start()
        pump(self.request, upstream)
        t.join()

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

Server(('127.0.0.1', port), Tunnel).serve_forever()
