#!/usr/bin/env python
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
import json
import message_loop
from trace_event import *

POLL_INTERVAL = 0.05

class ChromeShim(object):
  def __init__(self, browser):
    self.browser = browser
    message_loop.post_delayed_task(self.on_tick, POLL_INTERVAL)
    self._event_listeners = dict()
    self._loaded = False
    self._commands_to_run_when_loaded = []

    self.add_event_listener("console.log", self._on_console_log)

  def add_command_when_loaded(self, cb, *args):
    """Adds a command to run when the shim is active."""
    if self._loaded:
      cb(*args)
      return
    def do_it():
      cb(*args)
    self._commands_to_run_when_loaded.append(do_it)

  def _run_commands_to_run_when_loaded(self):
    assert self._loaded
    for cb in self._commands_to_run_when_loaded:
      cb()
    del self._commands_to_run_when_loaded[:]

  def add_event_listener(self, handler, cb, *args):
    def call_cb(*args):
      cb(*args)
    if handler not in self._event_listeners:
      self._event_listeners[handler] = []
    self._event_listeners[handler].append(call_cb)

  @tracedmethod
  def on_tick(self):
    try:
      # check for chrome_shim existing
      chrome_shim_exists = self.browser.run_javascript("(window['chrome'] !== undefined)") == 'true'
      if chrome_shim_exists:
        # check for sends
        sends = self.browser.run_javascript("chrome.get_pending_sends()")
        try:
          sends = json.loads(sends)
        except ValueError:
          sends = []

        for send in sends:
          if send["msg"] == '__chrome_shim_loaded':
            self._loaded = True
            self._run_commands_to_run_when_loaded()
          elif send["msg"] in self._event_listeners:
            for cb in self._event_listeners[send["msg"]]:
              cb(*send["args"])
          else:
            print "Unrecognized message from chrome.send: %s" % send["msg"]
    finally:
      message_loop.post_delayed_task(self.on_tick, POLL_INTERVAL)

  def _on_console_log(self, args):
    print "console: ", args

