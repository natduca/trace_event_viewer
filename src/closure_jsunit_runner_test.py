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
from closure_jsunit_runner import *

class ClosureJSUnitTestRunnerTest(ClosureJSUnitRunner):
  def test_timeout_successfully(self):
    self.assertRaises(Exception, lambda: self.go("closure_jsunit_runner_test_timeout.html",timeout=0.5))

  def test_fails_successfully(self):
    self.assertRaises(Exception, lambda: self.go("closure_jsunit_runner_test.html?runTests=test_that_fails"))

  def test_raise_throws(self):
    self.assertRaises(Exception, lambda: self.go("closure_jsunit_runner_test.html?runTests=test_that_throws"))

  def test_succeeds_successfully(self):
    self.go("closure_jsunit_runner_test.html?runTests=test_that_succeeds")
