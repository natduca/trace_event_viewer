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
import browser
import deps
import message_loop
import unittest
import urllib

from frontend_download import FrontendDownload
from frontend_daemon_host import FrontendDaemonHost

__all__ = ["ClosureJSUnitRunner"]

_dl = None

POLL_RATE = 0.2
DEFAULT_TIMEOUT = 10

class ClosureJSUnitRunner(unittest.TestCase):
  """This class runs a test built on Google Closure's goog.testing.jsunit"""
  def go(self, test_path, timeout = DEFAULT_TIMEOUT):
    self._drop_timeout = False
    self.test_path = test_path
    global _dl
    self.host = None
    try:
      if not _dl:
        _dl = FrontendDownload(deps.CHROME_SVN_BASE, deps.CHROME_SVN_REV)
      self.host = FrontendDaemonHost(23252, _dl.data_dir)
      self.browser = browser.Browser()
      u = urllib.basejoin(self.host.baseurl, self.test_path)
      self.browser.load_url(u)
      self.browser.show()
      message_loop.post_delayed_task(self.on_tick, POLL_RATE)
      message_loop.post_delayed_task(self.on_timeout, timeout)
      message_loop.run_main_loop()
    finally:
      if self.host:
        self.host.close() # prevent host from leaking its daemon

  def on_tick(self):
    # check for gtest existing... BE CAREFUL --- wxpython crashes if it gets
    gtest_exists = self.browser.run_javascript("(window['G_testRunner'] !== undefined)") == 'true'
    if gtest_exists:
      # check for status
      gtest_finished = self.browser.run_javascript("G_testRunner.isFinished()") == 'true'

      if gtest_finished:
        success = self.browser.run_javascript("G_testRunner.isSuccess()") == 'true'
        if success:
          message_loop.quit_main_loop()
          return
        else:
          if browser.debug_mode:
            self._drop_timeout = True
            return
          if self.test_path.find('closure_jsunit_runner_test') != -1:
            raise Exception("_noprint Test %s failed" % self.test_path)
          else:
            raise Exception("Test %s failed" % self.test_path)

    message_loop.post_delayed_task(self.on_tick, POLL_RATE)

  def on_timeout(self):
    if self._drop_timeout:
      return
    if self.test_path.find('closure_jsunit_runner_test') != -1:
      raise Exception("_noprint Test %s timed out" % self.test_path)
    else:
      raise Exception("Test %s timed out" % self.test_path)

  def cleanUp(self):
    if self.host:
      self.host.close() # prevent host from leaking its daemon
