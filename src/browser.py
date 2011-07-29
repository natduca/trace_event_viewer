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
import traceback

# try using gtk
_has_gtk = False
try:
  import pygtk
  pygtk.require('2.0')
  _has_gtk = True
except ImportError:
  pass

# if that didn't work, try using wx
_has_wx = False
try:
  import wx
  _has_wx = True
except ImportError:
  pass

class BrowserBase(object):
  def __init__(self, baseurl):
    pass


if _has_gtk:
  import browser_gtk as platform_browser
elif _has_wx:
  import browser_wx as platform_browser


def post_task(cb, *args):
  platform_browser.post_task(cb, *args)

def run_main_loop():
  platform_browser.run_main_loop()

def quit_main_loop():
  platform_browser.quit_main_loop()

def Browser(*args):
  if _has_gtk:
    return platform_browser.Browser(*args)
  elif _has_wx:
    return platform_browser.Browser(*args)
  else:
    raise Exception("No GUI toolkit found")

