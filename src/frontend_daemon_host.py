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
import frontend_resources
import httplib
import json
import logging
import os
import socket
import subprocess
import sys
import time
import urllib
import urllib2
from trace_event import *

def is_port_listening(port):
  import socket
  s = socket.socket()
  try:
    s.connect(('localhost', port))
  except socket.error:
    return False
  s.close()
  return True

class FrontendDaemonHost(object):
  @tracedmethod
  def __init__(self, port, resources):
    # If a daemon is running, try killing it via /kill
    if is_port_listening(port):
      for i in range(2):
        logging.warning("Existing daemon found. Asking it to exit")
        try:
          conn = httplib.HTTPConnection('localhost', port, True)
          conn.request('GET', '/exit')
        except:
          break
        res = conn.getresponse()
        if res.status != 200:
          break
        else:
          time.sleep(0.2)

    if is_port_listening(port):
      raise Exception("Daemon running")
    self._port = port

    topdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    args = [sys.executable, "-m", "src.frontend_daemon"]
    if trace_is_enabled():
      args.extend(["--trace", "./%s.trace" % sys.argv[2]])
    args.append(str(port))
    for mapbase,mapto in resources.items():
      args.append(mapbase)
      abs_mapto = os.path.abspath(mapto)
      args.append(abs_mapto)
    self._daemon_proc = subprocess.Popen(args, cwd=topdir)
    try:
      self._wait_for_daemon_start()
    except Exception, ex:
      import traceback
      traceback.print_exc()
      self.close()
      raise ex

  @tracedmethod
  def _wait_for_daemon_start(self):
    ok = False
    for i in range(10):
      try:
        conn = httplib.HTTPConnection('localhost', self._port, True)
        conn.request('GET', '/ping')
      except:
        time.sleep(0.05)
        continue

      res = conn.getresponse()
      if res.status != 200:
        ok = False
        break
      if res.read() != 'OK':
        ok = False
        break
      ok = True
      break
    if not ok:
      raise Exception("Daemon did not come up")

    self._conn = None
    self._db_proxy = None

  @tracedmethod
  def close(self):
    try:
      pass
      conn = httplib.HTTPConnection('localhost', self._port, True)
      conn.request('GET', '/exit')
    except:
      pass
    t_beginning = time.time()
    while True:
      if self._daemon_proc.poll() is not None:
        break
      seconds_passed = time.time() - t_beginning
      if seconds_passed > 0.5:
        self._daemon_proc.terminate()
        self._daemon_proc.wait()
        break
      time.sleep(0.1)


  @property
  def host(self):
    # Report as an IP address because on older webkit builds that use soup, localhost
    # does not work as a URL.
    return socket.gethostbyname('localhost')

  @property
  def port(self):
    return self._port

  @property
  def baseurl(self):
    return 'http://%s:%i' % (self.host, self._port)

  def urlread(self, path):
    return urllib2.urlopen(urllib.basejoin(self.baseurl, path)).read()
