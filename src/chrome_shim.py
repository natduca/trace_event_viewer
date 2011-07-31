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

POLL_INTERVAL = 0.05

class ChromeShim(object):
  def __init__(self, browser):
    self.browser = browser
    message_loop.post_delayed_task(self.on_tick, POLL_INTERVAL)
    self._event_listeners = dict()

  def add_event_listener(self, handler, cb, *args):
    def call_cb(*args):
      cb(*args)
    if handler not in self._event_listeners:
      self._event_listeners[handler] = []
    self._event_listeners[handler].append(call_cb)
    
  def on_tick(self):
    try:
      # check for chrome_shim existing
      chrome_shim_exists = self.browser.run_javascript("(window['chrome'] !== undefined)") == 'true'
      if chrome_shim_exists:
        # check for sends
        sends = self.browser.run_javascript("chrome.get_pending_sends()")
        sends = json.loads(sends)
        for send in sends:
          if send["msg"] in self._event_listeners:
            for cb in self._event_listeners[send["msg"]]:
              cb(*send["args"])
          else:
            print "Unrecognized send: %s" % cb
    finally:
      message_loop.post_delayed_task(self.on_tick, POLL_INTERVAL)

