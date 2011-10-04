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
import unittest

class _TestThatTimesOut(ClosureJSUnitRunner):
  def test(self):
    self.go("/src/closure_jsunit_runner_test_timeout.html",timeout=0.5)

class _TestThatFails(ClosureJSUnitRunner):
  def test(self):
    self.go("/src/closure_jsunit_runner_test.html?runTests=test_that_fails")

class _TestThatThrows(ClosureJSUnitRunner):
  def test(self):
    self.go("/src/closure_jsunit_runner_test.html?runTests=test_that_throws")

class _TestThatSucceeds(ClosureJSUnitRunner):
  def test(self):
    self.go("/src/closure_jsunit_runner_test.html?runTests=test_that_succeeds")

class ClosureJSUnitRunnerTest(unittest.TestCase):
  def test_test_that_times_out(self):
    test = _TestThatTimesOut("test")
    result = unittest.TestResult()
    test.run(result)
    self.assertFalse(result.wasSuccessful())
    self.assertEquals(0, len(result.failures))
    self.assertEquals(1, len(result.errors))

  def test_test_that_fails(self):
    test = _TestThatFails("test")
    result = unittest.TestResult()
    test.run(result)
    self.assertFalse(result.wasSuccessful())
    # FIXME: Right now, JSUnit failures are reported the same as errors.
    self.assertEquals(0, len(result.failures))
    self.assertEquals(1, len(result.errors))

  def test_test_that_throws(self):
    test = _TestThatThrows("test")
    result = unittest.TestResult()
    test.run(result)
    self.assertFalse(result.wasSuccessful())
    self.assertEquals(0, len(result.failures))
    self.assertEquals(1, len(result.errors))

  def test_test_that_succeeds(self):
    test = _TestThatSucceeds("test")
    result = unittest.TestResult()
    test.run(result)
    self.assertTrue(result.wasSuccessful())
