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
import closure_jsunit_runner
import frontend_daemon
import unittest
import os

class FrontendDaemonTest_Basic(unittest.TestCase):
  def test_daemon(self):
    d = frontend_daemon.FrontendDaemon("", 12345, {})
    d.try_handle_request(0.1)
    d.shutdown()

  def test_maps(self):
    d = frontend_daemon.FrontendDaemon("", 12345, {"/a": "./a"})
    self.assertEquals(None, d.resolve_path("foo"))
    self.assertEquals(None, d.resolve_path("/c"))
    self.assertEquals(None, d.resolve_path("/a/../d"))
    self.assertEquals(None, d.resolve_path("/ab"))
    self.assertEquals(os.path.abspath("./a/d"), d.resolve_path("/a/d"))
    d.try_handle_request(0.1)
    d.shutdown()

  def test_maps_with_root(self):
    d = frontend_daemon.FrontendDaemon("", 12345, {"/a": "./a", "/": "./foo"})
    self.assertEquals(None, d.resolve_path("/.."))
    self.assertEquals(None, d.resolve_path("//"))
    self.assertEquals(os.path.abspath("./foo/c"), d.resolve_path("/c"))
    self.assertEquals(None, d.resolve_path("/a/../d"))
    self.assertEquals(os.path.abspath("./foo/ab"), d.resolve_path("/ab"))
    self.assertEquals(os.path.abspath("./a/d"), d.resolve_path("/a/d"))
    d.try_handle_request(0.1)
    d.shutdown()


class FrontendDaemonTest_JSUnit(closure_jsunit_runner.ClosureJSUnitRunner):
  def test_webkit_fixups(self):
    self.go("/src/frontend_daemon_test.html")
