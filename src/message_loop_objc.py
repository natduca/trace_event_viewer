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
import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
import sys

_is_main_loop_running = False
_current_main_loop_instance = 0
_raise_exception_after_quit = False
_pending_tasks = [] # list of tasks added before the NSApplication runloop began
def _get_cur_app_delegate():
  return NSApplication.sharedApplication().delegate()

class AppDelegate(NSObject):
  def awakeFromNib(self):
    print "awake"
    for p in _pending_tasks:
      if p[2] > 0:
        self.performSelectorOnMainThread_withObject_waitUntilDone_(self.runtask, p, False)
      else:
        self.performSelector_withObject_afterDelay_(self.runtask, p, p[2])

  @objc.signature('v@:@')
  def runtask(self, p):
    global _current_main_loop_instance
    # timeouts that were enqueued when the mainloop exited should not run
    if _current_main_loop_instance == p[0]:
      p[1](*p[3])

  @objc.IBAction
  def open_(self, a):
    print "open"

  @objc.IBAction
  def applicationDidFinishLaunching_(self, a):
    print "didFinishLaunching"

  def quit_(self, a):
    print "quitting"

def post_task(cb, *args):
  p = (_current_main_loop_instance, cb, 0, args)
  if _is_main_loop_running:
    d = _get_cur_app_delegate()
    d.performSelectorOnMainThread_withObject_waitUntilDone_(d.runtask, p, False)
  else:
    _pending_tasks.append(p)

def post_delayed_task(cb, delay, *args):
  p = (_current_main_loop_instance, cb, delay, args)
  if _is_main_loop_running:
    d = _get_cur_app_delegate()
    d.performSelector_withObject_afterDelay_(d.runtask, p, p[2])
  else:
    _pending_tasks.append(p)

def _on_exception_while_in_main_loop(type, value, tb):
  message = 'Uncaught exception:\n'
  message += ''.join(traceback.format_exception(type, value, tb))
  print message
  quit_main_loop()

def is_main_loop_running():
  return _is_main_loop_running

def run_main_loop():
  global _current_main_loop_instance
  global _is_main_loop_running
  try:
    _is_main_loop_running = True
    AppHelper.runEventLoop(installInterrupt=True)
  finally:
    _is_main_loop_running = False
    _current_main_loop_instance += 1
  print "stop done"
  # todo, destroy any open windows
  windows = NSApplication.sharedApplication().windows()
  for w in windows:
    w.close()

  global _raise_exception_after_quit
  if _raise_exception_after_quit:
    _raise_exception_after_quit = False
    raise Exception("An exception occured while running main loop.")

def quit_main_loop(quit_with_exception):
  global _raise_exception_after_quit
  global _current_main_loop_instance
  if quit_with_exception:
    _raise_exception_after_quit = True
  _current_main_loop_instance += 1 # stop any in-flight tasks in case the objc stuff doesn't die promptly
  AppHelper.stopEventLoop()
  print "stop requested"
