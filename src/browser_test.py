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
import os
import unittest
from frontend_daemon_host import FrontendDaemonHost

class BrowserTest(unittest.TestCase):
  def setUp(self):
    self.host = FrontendDaemonHost(12345, os.getcwd())
    self.browser = browser.Browser()

  def test_browser(self):
    self.browser.Show()
    def step2():
      self.assertTrue(browser.is_main_loop_running())
      browser.quit_main_loop()
    browser.post_task(step2)
    browser.run_main_loop()

  def test_delayed_task(self):
    self.browser.Show()
    def step2():
      browser.quit_main_loop()
    browser.post_delayed_task(step2, 0.1)
    browser.run_main_loop()

  def test_run_javascript(self):
    self.browser.Show()
    def step2():
      ret = self.browser.run_javascript("1 + 1")
      self.assertEquals("2", ret)
      browser.quit_main_loop()
    browser.post_delayed_task(step2, 0.1)
    browser.run_main_loop()

  def test_exception_stops_test(self):
    self.browser.Show()
    def step2():
      raise Exception, "_noprint expected exception" # _noprint is trapped by run_tests and supresses print
    browser.post_delayed_task(step2, 0.1)
    self.assertRaises(Exception, lambda: browser.run_main_loop())

  def test_assert_failing_stops_test(self):
    self.browser.Show()
    def step2():
      self.assertFalse(True,msg="_noprint")
    browser.post_delayed_task(step2, 0.1)
    self.assertRaises(Exception, lambda: browser.run_main_loop())

  def tearDown(self):
    self.host.close()
