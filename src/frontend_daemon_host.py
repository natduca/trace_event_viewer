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
import Queue
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

class FrontendDaemonHostThread(threading.Thread):
  def __init__(self, port, resources, init_event):
    threading.Thread.__init__(self)
    self._port = port
    self._resources = resources
    self._init_event = init_event
    self._run = False
    self._thread_commands = Queue.Queue()

  def run(self):
    self._daemon = frontend_daemon.FrontendDaemon("", self._port, self._resources)
    self._init_event.set()

    self._run = True
    while self._run:
      self._run_once()
    self._daemon.server_close()

  @tracedmethod
  def _run_once(self):
    self._daemon.try_handle_request(0.2)
    while True:
      try:
        cmd = self._thread_commands.get_nowait()
      except Queue.Empty:
        break
      cmd[0](*cmd[1:])

  @tracedmethod
  def add_mapped_path(self, mapbase, mapto):
    completion = threading.Event()
    self._thread_commands.put((self._add_mapped_path_on_thread, mapbase, mapto, completion))
    completion.wait()

  @tracedmethod
  def _add_mapped_path_on_thread(self, mapbase, mapto, completion):
    self._daemon.add_mapped_path(mapbase, mapto)
    completion.set()

  def stop(self):
    self._run = False

class FrontendDaemonHost(object):

  @tracedmethod
  def __init__(self, port, resources):
    if is_port_listening(port):
      raise Exception("Cannot start, port %i in use." % port)

    self._port = port

    init_event = threading.Event()
    self._thread = FrontendDaemonHostThread(port, resources, init_event)
    self._thread.start()
    init_event.wait()

  @tracedmethod
  def close(self):
    self._thread.stop()
    self._thread.join()
    self._thread = None

  @tracedmethod
  def add_mapped_path(self, mapbase, mapto):
    self._thread.add_mapped_path(mapbase, mapto)

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
