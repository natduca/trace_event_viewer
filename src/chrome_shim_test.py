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
import chrome_shim
import deps
import message_loop
import unittest
import urllib

from frontend_download import FrontendDownload
from frontend_daemon_host import FrontendDaemonHost

DEFAULT_TIMEOUT = 10

class ChromeShimTest(unittest.TestCase):
  """
  This class runs a page, adds a ChromeShim to it,
  and makes sure we receive sends from it
  """
  def test_shim(self):
    self.test_path = "/chrome_shim_test.html";
    self.host = None
    try:
      dl = FrontendDownload(deps.CHROME_SVN_BASE, deps.CHROME_SVN_REV)
      self.host = FrontendDaemonHost(23252, dl.data_dir)
      self.browser = browser.Browser()
      u = urllib.basejoin(self.host.baseurl, self.test_path)
      self.browser.load_url(u)
      self.browser.show()
      self.shim = chrome_shim.ChromeShim(self.browser)
      self.shim.add_event_listener('foo1', self.on_foo1)
      self.shim.add_event_listener('foo2', self.on_foo2)
      message_loop.post_delayed_task(self.on_timeout, DEFAULT_TIMEOUT)
      message_loop.run_main_loop()
    finally:
      if self.host:
        self.host.close() # prevent host from leaking its daemon

  def on_foo1(self):
    self.got_foo1 = True

  def on_foo2(self, arg):
    self.assertEquals('bar', arg)
    self.assertTrue(self.got_foo1)
    message_loop.quit_main_loop()

  def on_timeout(self):
    raise Exception("Test %s timed out" % self.test_path)

  def cleanUp(self):
    if self.host:
      self.host.close() # prevent host from leaking its daemon

