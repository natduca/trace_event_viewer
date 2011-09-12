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

_objc_enabled = False

def main():
  usage = "Usage: %prog [options] trace_file"
  parser = optparse.OptionParser(usage=usage)
  parser.add_option(
      '-v', '--verbose', action='count', default=0,
      help='Increase verbosity level (repeat as needed)')
  parser.add_option('--debug', dest='debug', action='store_true', default=False, help='Break into pdb when an assertion fails')
  parser.add_option('--chrome', dest='chrome_path', default=None, help='Instead of getting a copy of the viewer from chromium via chromium.org, use this path instead')
  parser.add_option('--objc', dest='objc', action='store_true', default=False, help='Enable experimental support for PyObjC-based GUI')
  (options, args) = parser.parse_args()

  global _objc_enabled
  if options.objc:
    print "foo"
    _objc_enabled = True

  import message_loop
  if not message_loop.has_toolkit:
    if _objc_enabled:
      print """No supported GUI toolkit found. Trace_event_viewer supports PyGtk, WxPython and PyObjC"""
    else:
      print """No supported GUI toolkit found. Trace_event_viewer supports PyGtk and WxPython"""
    return -1

  if options.verbose >= 2:
    logging.basicConfig(level=logging.DEBUG)
  elif options.verbose:
    logging.basicConfig(level=logging.INFO)
  else:
    logging.basicConfig(level=logging.WARNING)

  # these imports are held until the main function because we want to avoid side effects when
  # settings up the command line.
  import re
  import urllib
  import browser as browser
  import deps as deps
  import frontend_resources as frontend_resources
  import frontend_daemon_host as frontend_daemon_host
  import message_loop as message_loop
  import chrome_shim as chrome_shim

  if options.debug:
    browser.debug_mode = True

  if len(args) > 1:
    print "Can only load one file at a time"
    return 255
  if len(args) == 0:
    print "Expected: trace_file."
    return 255
  trace_data = open(args[0]).read()

  # detect array formats
  if trace_data.startswith('['):
    trace_data = trace_data.strip()
    if trace_data.endswith(']'):
      trace_data = """{"traceEvents": %s}""" % trace_data
    else:
      # its an array, but the close ] is missing, which we allow
      trace_data = """{"traceEvents": %s]}""" % trace_data      
  if trace_data.find('\n') != -1:
    trace_data = trace_data.replace('\n', '')

  if options.chrome_path:
    options.chrome_path = os.path.expanduser(options.chrome_path)
    ok = True
    ok &= os.path.exists(os.path.join(options.chrome_path, "chrome/browser/resources/gpu_internals.html"))
    ok &= os.path.exists(os.path.join(options.chrome_path, "chrome/browser/resources/shared/js/cr.js"))
    if not ok:
      print "--chrome should point to the base chrome 'src' directory"
      return 0
    options.chrome_path = os.path.join(options.chrome_path, "chrome/browser/resources")

  host = None
  try:
    if options.chrome_path:
      fer = frontend_resources.FrontendResources(options.chrome_path)
    else:
      fer = frontend_resources.FrontendResources()
    host = frontend_daemon_host.FrontendDaemonHost(23252, fer.dir_mappings)
    b = browser.Browser()
    shim = chrome_shim.ChromeShim(b)
    b.load_url(urllib.basejoin(host.baseurl, "/src/index.html"))
    b.show()
    if len(args) == 1:
      def do_load():

        res = b.run_javascript("loadTrace(JSON.parse('%s'))" % trace_data);
        if res != 'true':
          raise Exception('LoadTrace failed with %s', res)
      shim.add_event_listener('ready', do_load)
    message_loop.run_main_loop()
  finally:
    if host:
      host.close() # prevent host from leaking its daemon
  return 0

def run():
  if sys.argv[1] != '--main-name':
    raise Exception("launched wrong")
  main_name = sys.argv[2]
  del sys.argv[1:2]
  if main_name == 'trace_viewer':
    main()
  else:
    raise "Unrecognized main name: %s" % main_name

def bootstrap_main(main_name):
  if sys.platform == 'darwin':
    if ('--triedenv' not in sys.argv) and ('--triedarch' not in sys.argv):
      import objc_stub
      objc_stub.try_to_exec_stub(main_name)

    # To use wx-widgets on darwin, we need to be in 32 bit mode. Import of wx
    # will fail if you run python in 64 bit mode, which is default in 10.6+. :'(
    # It is depressingly hard to force python into 32 bit mode reliably across
    # computers, for some reason. So, we try two approaches known to work... one
    # after the other.
    wx_found_but_failed = False
    try:
      import wx
    except ImportError:
      if str(sys.exc_value).find("no appropriate 64-bit"):
        wx_found_but_failed = True

    if wx_found_but_failed:
      # try using the versioner trick
      if '--triedenv' not in sys.argv:
        os.putenv('VERSIONER_PYTHON_PREFER_32_BIT', 'yes')
        args = [sys.executable, sys.argv[0], '--triedenv']
        args.extend(sys.argv[1:])
        os.execve(args[0], args, os.environ)

      # last chance...
      if '--triedarch' not in sys.argv:
        args = ["/usr/bin/arch", "-i386", sys.executable, sys.argv[0], '--triedarch']
        args.extend(sys.argv[1:])
        os.execv(args[0], args)

      # did we already try one of the tricks below? Bail out to prevent recursion...
      print "Your system's python is 64 bit, and all the tricks we know to get it into 32b mode failed."
      sys.exit(255)

    else:
      try:
        sys.argv.remove('--triedenv')
      except:
        pass
      try:
        sys.argv.remove('--triedarch')
      except:
        pass
      import src
      sys.argv.insert(1, '--main_name')
      sys.argv.insert(2, main_name)
      sys.exit(run())

  else:
    import src
    sys.argv.insert(1, '--main_name')
    sys.argv.insert(2, main_name)
    sys.exit(run())
