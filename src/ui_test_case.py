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
import message_loop
import os
import subprocess
import sys
import tempfile
import unittest

class UITestCase(unittest.TestCase):
  def __init__(self, method_name, is_in_slave = False):
    unittest.TestCase.__init__(self, method_name)
    self._method_name = method_name
    self._is_in_slave = is_in_slave
    
  def run(self, result):
    if sys.platform == 'darwin' and '--objc' in sys.argv and not self._is_in_slave:
      return self.run_darwin(result)
    message_loop.set_active_test(self, result)
    unittest.TestCase.run(self, result)
    message_loop.set_active_test(None, None)
      
  def run_darwin(self, testResult):
    mod = __import__(self.__class__.__module__, {},{},fromlist=[True])
    # if this pops, then your test class wasn't on the module, which is required for this test system
    try:
      cls = getattr(mod, self.__class__.__name__) 
    except AttributeError:
      raise AttributeError("Your class must be a member of the enclosing module %s." % self.__class__.__module__)
    assert cls == self.__class__

    result = tempfile.NamedTemporaryFile()
    basedir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
    trace_viewer_stub_app = os.path.join(basedir, "./support/trace_viewer_stub.app/Contents/MacOS/trace_viewer_stub")
    args = [trace_viewer_stub_app,
            "--main-name", "src.ui_test_case",
            "--module", self.__class__.__module__,
            "--class", self.__class__.__name__,
            "--method", self._method_name,
            "--result", result.name]
    if '--objc' in sys.argv:
      args.append('--objc')
    self._slave_proc = subprocess.Popen(args, cwd=basedir)

    # todo, add timeout...
    try:
      self._slave_proc.wait()
    finally:
      if self._slave_proc.poll() == None:
        self._slave_proc.kill()

    f = open(result.name, 'r')
    r = f.read()
    f.close()
    result.close()

    try:
      childTestResult = eval(r)
    except:
      print "could not eval [%s]" % r
      raise
    testResult.startTest(self)
    for e in childTestResult["errors"]:
      testResult.errors.append((self, e)) # use this directly because addError treats the passed-in value as an exc_info
    for e in childTestResult["failures"]:
      testResult.failures.append((self, e)) # use this directly because addFailure the passed-in value as an exc_info
    if childTestResult["shouldStop"]:
      testResult.stop()
    testResult.stopTest(self)
    
def main_usage():
  return "Usage: %prog"

def main(parser):
  parser.add_option("--module", dest="module")
  parser.add_option("--class", dest="cls")
  parser.add_option("--method", dest="method")
  parser.add_option("--result", dest="result")
  (options, args) = parser.parse_args()
  
  mod = __import__(options.module, {},{},fromlist=[True])
  cls = getattr(mod, options.cls)
  test = cls(options.method, is_in_slave = True)
  result = unittest.TestResult()
  import message_loop_objc
  _output_ran = []
  def output_result():
    f = open(options.result, 'w')
    s = repr({
      "testsRun": result.testsRun,
      "errors": [e for t,e in result.errors],
      "failures": [e for t,e in result.failures],
      "shouldStop": result.shouldStop})
    f.write(s)
    f.close()
    _output_ran.append(True)
  message_loop.set_unittests_running(True)
  message_loop_objc.add_quit_handler(output_result)
  test.run(result)
  message_loop.set_unittests_running(False)
  if len(_output_ran) == 0:
    output_result()
  sys.exit(0)
