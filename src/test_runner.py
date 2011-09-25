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
import logging
import message_loop
import optparse
import os
import platform
import re
import sys
import types
import traceback
import unittest

def discover(filters):
  # poor mans unittest.discover, but that ignores classes
  # that start with _
  loader = unittest.TestLoader()
  subsuites = []

  for (dirpath, dirnames, filenames) in os.walk('src'):
    for filename in [x for x in filenames if re.match('.*_test\.py$', x)]:
      if filename.startswith('.') or filename.startswith('_'):
        continue
      fqn = dirpath.replace('/', '.') + '.' + re.match('(.+)\.py$', filename).group(1)

      # load the module
      try:
        module = __import__(fqn,fromlist=[True])
      except:
        print "While importing [%s]\n" % fqn
        traceback.print_exc()
        continue

      def test_is_selected(name):
        for f in filters:
          if re.search(f,name):
            return True
        return False

      if hasattr(module, 'suite'):
        base_suite = module.suite()
      else:
        base_suite = loader.loadTestsFromModule(module)
      new_suite = unittest.TestSuite()
      for t in base_suite:
        if isinstance(t, unittest.TestSuite):
          for i in t:
            # skip test classes that start with an underscore
            if i.__class__.__name__.startswith("_"):
              continue
            if test_is_selected(i.id()):
              new_suite.addTest(i)
        elif isinstance(t, unittest.TestCase):
          if test_is_selected(t.id()):
            new_suite.addTest(t)
        else:
          raise Exception("Wtf, expected TestSuite or TestCase, got %s" % t)

      if new_suite.countTestCases():
        subsuites.append(new_suite)

  return unittest.TestSuite(subsuites)

def main_usage():
  return "Usage: run_tests [options] [regexp of tests to run]"

def main(parser):
  parser.add_option('--debug', dest='debug', action='store_true', default=False, help='Break into pdb when an assertion fails')
  parser.add_option('-i', '--incremental', dest='incremental', action='store_true', default=False, help='Run tests one at a time.')
  parser.add_option('-s', '--stop', dest='stop_on_error', action='store_true', default=False, help='Stop running tests on error.')
  (options, args) = parser.parse_args()

  # install hook on set_trace if --debug
  if options.debug:
    import exceptions
    class DebuggingAssertionError(exceptions.AssertionError):
      def __init__(self, *args):
        exceptions.AssertionError.__init__(self, *args)
        print "Assertion failed, entering PDB..."
        import pdb
        if hasattr(sys, '_getframe'):
          pdb.Pdb().set_trace(sys._getframe().f_back.f_back)
        else:
          pdb.set_trace()
    unittest.TestCase.failureException = DebuggingAssertionError

    def hook(*args):
      import traceback, pdb
      traceback.print_exception(*args)
      pdb.pm()
    sys.excepthook = hook

    import browser
    browser.debug_mode = True

  # make sure cwd is the base directory!
  os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

  if len(args) > 0:
    suites = discover(args)
  else:
    suites = discover(['.*'])

  r = unittest.TextTestRunner()
  if not options.incremental:
    message_loop.set_unittests_running(True)
    res = r.run(suites)
    message_loop.set_unittests_running(False)
    if res.wasSuccessful():
      return 0
    return 255
  else:
    message_loop.set_unittests_running(True)
    ok = True
    for s in suites:
      if isinstance(s, unittest.TestSuite):
        for t in s:
          print '----------------------------------------------------------------------'
          print 'Running %s' % str(t)
          res = r.run(t)
          if not res.wasSuccessful():
            ok = False
            if options.stop_on_error:
              break
        if ok == False and options.stop_on_error:
          break
      else:
        res = r.run(s)
        if not res.wasSuccessful():
          ok = False
          if options.stop_on_error:
            break
    message_loop.set_unittests_running(False)
    if ok:
      return 0
    return 255

