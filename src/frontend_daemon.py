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

    rpath = os.path.realpath(os.path.join(os.getcwd(), path[1:]))
    if not rpath.startswith(os.getcwd()) or not os.path.exists(rpath):
      self.send(404)
      return
    if rpath.endswith('.html'):
      data = open(rpath, 'r').read()
      data2 = re.sub('(\<head.*\>)', """\g<1>
<script src="/webkit_shim.js"></script>
<script src="/es5-shim.js"></script>
<script src="/chrome_shim.js"></script>""", data)
      self.send(200, data2, content_type='text/html')
      return
    SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

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
  def __init__(self, host, port):
    BaseHTTPServer.HTTPServer.__init__(self, (host, port), _RequestHandler)
    self.port_ = port

  def on_exit(self, m, verb, data):
    logging.info("Exiting upon request.")
    self.shutdown()

  def serve_forever(self):
    self.is_running_ = True
    while self.is_running_:
      self.try_handle_request(0.2)

  def try_handle_request(self, delay):
    r, w, e = select.select([self], [], [], delay)
    if r:
      self.handle_request()

  def shutdown(self):
    self.is_running_ = False
    self.server_close()
    return 1


if __name__ == "__main__":
  port = int(sys.argv[1])
  basedir = sys.argv[2]

  os.chdir(basedir)
  daemon = FrontendDaemon("", port)
  daemon.serve_forever()
  sys.exit(0)
