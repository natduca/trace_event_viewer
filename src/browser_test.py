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
import browser
import frontend_resources
import message_loop
import os
import unittest

from frontend_daemon_host import FrontendDaemonHost

class BrowserTest(unittest.TestCase):
  def setUp(self):
    self.host = FrontendDaemonHost(12345, {"/": os.getcwd()})
    self.browser = browser.Browser()

  def test_browser(self):
    self.browser.show()
    def step2():
      self.assertTrue(message_loop.is_main_loop_running())
      message_loop.quit_main_loop()
    message_loop.post_task(step2)
    message_loop.run_main_loop()

  def test_delayed_task(self):
    self.browser.show()
    def step2():
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(step2, 0.1)
    message_loop.run_main_loop()

  def test_run_javascript(self):
    self.browser.show()
    def step2():
      ret = self.browser.run_javascript("1 + 1", require_loaded=False)
      self.assertEquals("2", ret)
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(step2, 0.1)
    message_loop.run_main_loop()

  def test_run_javascript_twice_with_same_result(self):
    """
    The gtk backend needs to do some magic to get return values.
    Asking for something with the same return value string is fragile.
    So, test that its working.
    """
    self.browser.show()
    def step2():
      ret = self.browser.run_javascript("1 + 2", require_loaded=False)
      self.assertEquals("3", ret)
      ret = self.browser.run_javascript("2 + 1", require_loaded=False)
      self.assertEquals("3", ret)
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(step2, 0.1)
    message_loop.run_main_loop()

  def test_run_javascript_that_results_in_json(self):
    """
    Make sure that the run_javascript method can handle complex inputs and outputs.
    """
    self.browser.show()
    def step2():
      ret = self.browser.run_javascript("""JSON.stringify({a: 3, b: 'foo', c: "bar"})""", require_loaded=False)
      self.assertEquals('{"a":3,"b":"foo","c":"bar"}', ret);
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(step2, 0.1)
    message_loop.run_main_loop()

  def test_run_javascript_that_throws(self):
    self.browser.show()
    def step2():
      ret = self.browser.run_javascript("""throw Error('Foo');""", require_loaded=False)
      # ret is pretty implmenetation specific, so best to just ensure it returns
      # todo, make the run_javascript throw ^_^
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(step2, 0.1)
    message_loop.run_main_loop()

  def test_run_javascript_that_wont_parse(self):
    self.browser.show()
    def step2():
      ret = self.browser.run_javascript("""'""", require_loaded=False)
      # ret is pretty implmenetation specific, so best to just ensure it returns
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(step2, 0.1)
    message_loop.run_main_loop()

  def test_run_javascript_with_newline(self):
    self.browser.show()
    def step2():
      ret = self.browser.run_javascript("""1+1\n""", require_loaded=False)
      # just ensure it returns
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(step2, 0.1)
    message_loop.run_main_loop()

  def tearDown(self):
    self.host.close()
