# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import re
import select
import sys
import time
import urlparse
import BaseHTTPServer
import SimpleHTTPServer

PORT = 8080


class _RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def __init__(self,*args):
    SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self,*args)

  def do_GET(self):
    (_, _, path, _, _) = urlparse.urlsplit(self.path)
    if path == "":
      path = "/"
    if not path.startswith("/"):
      raise Exception("Wtf")
    if path == "/exit":
      self.send(200, "OK")
      self.server.shutdown()
      return
    if path == "/ping":
      self.send(200, "OK")
      return

    resolved = self.server.resolve_path(path)
    if not resolved:
      self.send(404)
      return
    if not os.path.exists(resolved):
      self.send(404)
      return

    split = os.path.splitext(resolved)
    if split[1] in SimpleHTTPServer.SimpleHTTPRequestHandler.extensions_map:
      mimetype = SimpleHTTPServer.SimpleHTTPRequestHandler.extensions_map[split[1]]
    else:
      mimetype = "text/plain"

    if split[1].lower() == '.html':
      data = open(resolved, 'r').read()
      data2 = re.sub('(\<head.*\>)', """\g<1>
<script src="/src/webkit_shim.js"></script>
<script src="/es5-shim/es5-shim.js"></script>
<script src="/src/chrome_shim.js"></script>""", data)
      self.send(200, data2, mimetype)
    else:
      data = open(resolved, 'r').read()
      self.send(200, data, mimetype)

  def log_message(self, format, *args):
    logging.debug(format, args)

  def send(self, code, msg="",content_type="text/plain"):
    try:
      self.send_response(code)
      self.send_header('Last-Modified', self.date_time_string(time.time()))
      self.send_header('Content-Length', len(msg))
      self.send_header('Content-Type', content_type)
      self.end_headers()
      self.wfile.write(msg)
    except:
      pass

class FrontendDaemon(BaseHTTPServer.HTTPServer):
  def __init__(self, host, port, mapped_dirs):
    BaseHTTPServer.HTTPServer.__init__(self, (host, port), _RequestHandler)
    self._port = port
    self._mapped_dirs = dict()
    self._root_mappath = None
    for p,d in mapped_dirs.items():
      if p == "/":
        self._root_mappath = os.path.realpath(d)
      else:
        self._mapped_dirs[p] = os.path.realpath(d)

  def resolve_path(self, path):
    if path[0] != '/':
      return None

    for mapbase,mapto in self._mapped_dirs.items():
      if path.find(mapbase) != 0:
        continue
      subpath = path[len(mapbase):]
      if subpath[0] != '/':
        continue
      subpath = subpath[1:]
      candidate = os.path.abspath(os.path.join(mapto, subpath))
      if not candidate.startswith(mapto):
        return None
      return candidate

    if self._root_mappath:
      candidate = os.path.abspath(os.path.join(self._root_mappath, path[1:]))
      if not candidate.startswith(self._root_mappath):
        return None
      return candidate

  def on_exit(self, m, verb, data):
    logging.info("Exiting upon request.")
    self.shutdown()

  def serve_forever(self):
    self._is_running = True
    while self._is_running:
      self.try_handle_request(0.2)
    self.server_close()

  def try_handle_request(self, delay):
    r, w, e = select.select([self], [], [], delay)
    if r:
      self.handle_request()

  def shutdown(self):
    self._is_running = False
    return 1

if __name__ == "__main__":
  port = int(sys.argv[1])
  rest = sys.argv[2:]
  if len(rest) % 2 != 0:
    raise Exception("Must specify pairs of directories to map")
  mapped_dirs = {}
  for i in range(len(rest) / 2):
    p = rest[2*i]
    d = rest[2*i + 1]
    mapped_dirs[p] = d;
  daemon = FrontendDaemon("", port, mapped_dirs)
  daemon.serve_forever()
  sys.exit(0)
