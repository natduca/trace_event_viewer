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

def detect_toolkit():
  # try using gtk
  try:
    import pygtk
    pygtk.require('2.0')
    return (True, False)
  except ImportError:
    pass

  # if that didn't work, try using wx
  try:
    import wx
    return (False, True)
  except ImportError:
    pass

  return (False, False)

is_gtk, is_wx = detect_toolkit()


if is_gtk:
  import message_loop_gtk as platform_message_loop
elif is_wx:
  import message_loop_wx as platform_message_loop

def post_task(cb, *args):
  platform_message_loop.post_task(cb, *args)

def post_delayed_task(cb, delay, *args):
  platform_message_loop.post_delayed_task(cb, delay, *args)

def is_main_loop_running():
  return platform_message_loop.is_main_loop_running()

def run_main_loop():
  platform_message_loop.run_main_loop()

def quit_main_loop(quit_with_exception=False):
  platform_message_loop.quit_main_loop(quit_with_exception)
