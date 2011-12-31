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
import frontend_daemon
import frontend_resources
import httplib
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import urllib
import urllib2

def is_port_listening(port):
  import socket
  s = socket.socket()
  try:
    s.connect(('localhost', port))
  except socket.error:
    return False
  s.close()
  return True

class FrontendDaemonHostThread(threading.Thread):
  def __init__(self, port, resources, init_event):
    threading.Thread.__init__(self)
    self._port = port
    self._resources = resources
    self._init_event = init_event

  def run(self):
    self._daemon = frontend_daemon.FrontendDaemon("", self._port, self._resources)
    self._init_event.set()

    self._daemon.serve_forever()

  def stop(self):
    self._daemon.shutdown()

class FrontendDaemonHost(object):
  def __init__(self, port, resources):
    if is_port_listening(port):
      raise Exception("Cannot start, port %i in use." % port)

    self._port = port

    init_event = threading.Event()
    self._thread = FrontendDaemonHostThread(port, resources, init_event)
    self._thread.start()
    init_event.wait()


  def close(self):
    self._thread.stop()
    self._thread.join()
    self._thread = None

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
