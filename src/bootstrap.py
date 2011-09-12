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

def handle_args(options, args):
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

def run():
  if sys.argv[1] != '--main-name':
    raise Exception("launched wrong: expected --main-name <mainname> as first argument")
  main_name = sys.argv[2]
  del sys.argv[1:3] # remove the --main-name argument


  mod = __import__(main_name, {}, {}, True)
  parser = optparse.OptionParser(usage=mod.main_usage())
  parser.add_option(
      '-v', '--verbose', action='count', default=0,
      help='Increase verbosity level (repeat as needed)')
  parser.add_option('--debug', dest='debug', action='store_true', default=False, help='Break into pdb when an assertion fails')
  original_parse_args = parser.parse_args
  def parse_args_shim():
    options, args = original_parse_args()
    handle_args(options, args)
    return options, args
  parser.parse_args = parse_args_shim

  mod.main(parser)

def main(main_name):
  if sys.platform == 'darwin':
    if ('--objc' in sys.argv) and ('--triedenv' not in sys.argv) and ('--triedarch' not in sys.argv):
      import bootstrap_objc
      bootstrap_objc.try_to_exec_stub(main_name)

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
      sys.argv.insert(1, '--main-name')
      sys.argv.insert(2, main_name)
      sys.exit(run())

  else:
    import src
    sys.argv.insert(1, '--main-name')
    sys.argv.insert(2, main_name)
    sys.exit(run())
