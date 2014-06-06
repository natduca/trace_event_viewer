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
import optparse
import os
import sys

def _setupPathForModule(mod_dir, mod_name):
  path = os.path.join(
    os.path.dirname(__file__),
    "..", "third_party", mod_dir)
  if not os.path.exists(path):
    sys.stderr.write('Could not find %s\n' % os.path.relpath(path))
    sys.stderr.write('Did you forget git submodule update --init\n')
    sys.exit(1)
  if path not in sys.path:
    sys.path.append(path)
  try:
    __import__(mod_name, {}, {}, [])
  except ImportError:
    sys.stderr.write('Could not import %s from %s\n' % (mod_name, os.path.relpath(path)))
    sys.stderr.write('Did you forget git submodule update --init\n')
    sys.exit(1)

def _setupPath():
  _setupPathForModule("py-chrome-app", 'chromeapp')
  _setupPathForModule("py_trace_event", 'trace_event')
  _setupPathForModule("trace-viewer", 'trace_viewer.build')

_setupPath()

from trace_event import *
import chromeapp

class ViewerApp(object):
  def __init__(self, options, args):
    manifest_file = os.path.join(os.path.dirname(__file__),
                                 'chrome_app', 'manifest.json')
    self._app = chromeapp.App('trace-event-viewer',
                              manifest_file,
                              debug_mode=options.debug_mode)
    self._args = args
    self._app_instance = None

  def _InitInstance(self):
    self._app_instance.AddListener('load_nth_arg', self.OnLoadNthArg)
    self._timeline_view_js_file = os.path.join(os.path.dirname(__file__),
                                              'chrome_app', 'timeline_view.js')
    self._timeline_view_css_file = os.path.join(os.path.dirname(__file__),
                                              'chrome_app', 'timeline_view.css')

    import tvcm
    from trace_viewer.build import generate_standalone_timeline_view
    load_sequence = generate_standalone_timeline_view.CalcLoadSequence()
    with open(self._timeline_view_js_file, 'w') as f:
      f.write(tvcm.GenerateJS(load_sequence))
    with open(self._timeline_view_css_file, 'w') as f:
      f.write(tvcm.GenerateCSS(load_sequence))

  def _CleanupInstance(self):
    if os.path.exists(self._timeline_view_js_file):
      os.unlink(self._timeline_view_js_file)
    if os.path.exists(self._timeline_view_css_file):
      os.unlink(self._timeline_view_css_file)

  def OnLoadNthArg(self, args):
    index = args['index']
    filename = self._args[index]
    with open(filename, 'r') as f:
      return {'index': index,
              'trace': f.read()}

  def Run(self):
    with chromeapp.AppInstance(self._app, [len(self._args)]) as app_instance:
      try:
        self._app_instance = app_instance
        self._InitInstance()
        return self._app_instance.Run()
      finally:
        self._CleanupInstance()
        self._app_instance = None

def main(args):
  parser = optparse.OptionParser(
    usage="Usage: %prog [options] trace_file1 [trace_file2 ...]")
  parser.add_option('--trace', dest='trace', action='store_true', default=False, help='Records performance tracing information to %s.trace' % sys.argv[0])
  parser.add_option('--refresh-rate', '-r', dest='refresh_rate', action='store', default=60.0, help='The refresh rate for the screen, in hertz')
  parser.add_option('--debug', dest='debug_mode', action='store_true', default=False, help='Enables debugging features')
  (options, args) = parser.parse_args()

  if options.trace:
    trace_enable("./%s.trace" % sys.argv[0])

  if len(args) == 0:
    print "Expected: trace_file."
    return 255

  for a in args:
    if not os.path.exists(a):
      print "Trace file %s does not exist" % a
      return 255

  assert options.refresh_rate == 60
  app = ViewerApp(options, args)
  return app.Run()
