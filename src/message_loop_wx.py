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
import wx
import wx.webkit
import sys

_app = None
_current_main_loop_instance = 0
_raise_exception_after_quit = False

def _init_app():
  global _app
  if not _app:
    _app = wx.App(False)
    _app.SetAppName("TraceViewer")

_pending_tasks_timer = None
_pending_tasks = []
def _run_pending_tasks(e):
  pending = list(_pending_tasks)
  del _pending_tasks[:]
  for cb,args in pending:
    cb(*args)

def post_task(cb, *args):
  _init_app()
  global _pending_tasks_timer
  if not _pending_tasks_timer:
    _pending_tasks_timer = wx.Timer(None, -1)
    _pending_tasks_timer.Bind(wx.EVT_TIMER, _run_pending_tasks, _pending_tasks_timer)
  _pending_tasks.append( (cb, args) )

  if not _pending_tasks_timer.IsRunning():
    _pending_tasks_timer.Start(11, True)

def post_delayed_task(cb, delay, *args):
  _init_app()
  timer = wx.Timer(None, -1)
  main_loop_instance_at_post = _current_main_loop_instance
  def on_run(e):
    try:
      # timeouts that were enqueued when the mainloop exited should not run
      if _current_main_loop_instance == main_loop_instance_at_post:
        cb(*args)
    finally:
      timer.Destroy()
  timer.Bind(wx.EVT_TIMER, on_run, timer)
  timer.Start(max(1,int(delay * 1000)), True)

def _on_exception_while_in_main_loop(type, value, tb):
    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(type, value, tb))
    print message
    quit_main_loop()

def is_main_loop_running():
  if not _app:
    return False
  return _app.IsMainLoopRunning()

def run_main_loop():
  global _app
  global _current_main_loop_instance
  global _pending_tasks_timer
  _init_app()

  try:
    _app.MainLoop()
  finally:
    _current_main_loop_instance += 1

  for w in wx.GetTopLevelWindows():
    w.Destroy()
  _app.Destroy()
  del _pending_tasks[:]
  if _pending_tasks_timer:
    _pending_tasks_timer.Destroy()
    _pending_tasks_timer = None
  _app = None

  global _raise_exception_after_quit
  if _raise_exception_after_quit:
    _raise_exception_after_quit = False
    raise Exception("An exception occured while running main loop.")

def quit_main_loop(quit_with_exception):
  global _raise_exception_after_quit
  if quit_with_exception:
    _raise_exception_after_quit = True
  _app.ExitMainLoop()