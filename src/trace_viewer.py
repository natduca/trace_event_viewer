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

sys.path.append(os.path.join(os.path.dirname(__file__), "../third_party/py_trace_event/"))
try:
  from trace_event import *
except:
  print "Could not find py_trace_event. Did you forget 'git submodule update --init'"
  sys.exit(255)

def main_usage():
  return "Usage: %prog [options] trace_file1 [trace_file2 ...]"

def main(parser):
  parser.add_option('--chrome', dest='chrome_path', default=None, help='Instead of getting a copy of the viewer from chromium via chromium.org, use this path instead')
  parser.add_option('--debug', dest='debug', action='store_true', default=False, help='Add UI for JS debugging')
  parser.add_option('--trace', dest='trace', action='store_true', default=False, help='Records performance tracing information to %s.trace' % sys.argv[0])
  (options, args) = parser.parse_args()

  if options.trace:
    trace_enable("./%s.trace" % sys.argv[0])

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

  if len(args) == 0:
    print "Expected: trace_file."
    return 255

  if options.chrome_path:
    options.chrome_path = os.path.expanduser(options.chrome_path)
    ok = True
    ok &= os.path.exists(os.path.join(options.chrome_path, "chrome/browser/resources/tracing/timeline.js"))
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

    load_args = []
    for i in range(len(args)):
      u = "/file/%i" % i
      host.add_mapped_path(u, args[i])
      load_args.append("'%s'" % u)

    @trace
    def do_init():
      b = browser.Browser()
      shim = chrome_shim.ChromeShim(b)
      b.load_url(urllib.basejoin(host.baseurl, "/src/index.html"))
      b.show()

      @trace
      def do_load_via_url():
        logging.debug('Loading traces')
        load_args_str = ', '.join(load_args)
        res = b.run_javascript("loadTracesFromURLs([%s])" % load_args_str)

      @trace
      def on_load_failed():
        logging.error('Loading traces failed with %s' % res)
        print 'LoadTrace failed with %s' % res
        message_loop.quit_main_loop()

      @trace
      def on_load_done():
        logging.debug('Loading traces done.')

      shim.add_event_listener('ready', do_load_via_url)
      shim.add_event_listener('loadTracesFromURLs_Failed', on_load_failed)
      shim.add_event_listener('loadTracesFromURLs_Done', on_load_done)
    message_loop.post_task(do_init)
    message_loop.run_main_loop()
  finally:
    if host:
      host.close() # prevent host from leaking its thread
  return 0
