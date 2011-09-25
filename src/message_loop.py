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
import sys

# Two big TODOs for this system:
#  1. rename it to be an application, not a message loop. Sadly,
#     PyObjC is too constrained to support a real message loop abstraction,
#     so its better to just not provide such a mechanism in the first place.
#
#  2. refactor to be class based. Right now, its function based and fugly.

def detect_toolkit():
  # try using PyObjC on mac
  if sys.platform == 'darwin':
    if '--objc' in sys.argv:
      try:
        import objc
        return (False, False, True)
      except ImportError:
        pass

  # try using gtk
  try:
    import pygtk
    pygtk.require('2.0')
    return (True, False, False)
  except ImportError:
    pass

  # if that didn't work, try using wx
  try:
    import wx
    return (False, True, False)
  except ImportError:
    pass

  return (False, False, False)

is_gtk, is_wx, is_objc = detect_toolkit()

has_toolkit = is_gtk or is_wx or is_objc

if is_gtk:
  import message_loop_gtk as platform_message_loop
elif is_wx:
  import message_loop_wx as platform_message_loop
elif is_objc:
  import message_loop_objc as platform_message_loop


def post_task(cb, *args):
  platform_message_loop.post_task(cb, *args)

def post_delayed_task(cb, delay, *args):
  platform_message_loop.post_delayed_task(cb, delay, *args)

def is_main_loop_running():
  return platform_message_loop.is_main_loop_running()

def init_main_loop():
  platform_message_loop.init_main_loop()

def run_main_loop():
  """
  Runs the main loop. Note, this is not guaranteed to return on all platforms.
  You should never call this in unit tests --- if you have a test that requires
  UI or that wants to do asynchronous tests, derive from UITestcase which will
  call this for you.
  """
  platform_message_loop.run_main_loop()

def add_quit_handler(cb):
  platform_message_loop.add_quit_handler(cb)

def quit_main_loop():
  """
  Tries to quit the main loop. Note, think of this as quitting the application,
  not quitting the loop and returning to the run_main_loop caller. This is how a
  sane operating system works. However, this code works on OSX.
  """
  platform_message_loop.quit_main_loop()

def set_unittests_running(running):
  platform_message_loop.set_unittests_running(running)

def set_active_test(test, result):
  platform_message_loop.set_active_test(test, result)
