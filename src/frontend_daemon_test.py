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
import unittest
from closure_jsunit_runner import *
from frontend_daemon import FrontendDaemon


class FrontendDaemonTest_Basic(unittest.TestCase):
  def test_daemon(self):
    d = FrontendDaemon("", 12345)
    d.try_handle_request(0.1)
    d.shutdown()

class FrontendDaemonTest_JSUnit(ClosureJSUnitRunner):
  def test_webkit_fixups(self):
    self.go("frontend_daemon_test.html")
