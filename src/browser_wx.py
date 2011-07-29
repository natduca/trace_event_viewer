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

from browser import BrowserBase

_app = None
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
    try:
      cb(*args)
    except Exception, ex:
      import traceback
      traceback.print_exc()
      had_ex = True

def post_task(cb, *args):
  _init_app()
  global _pending_tasks_timer
  if not _pending_tasks_timer:
    _pending_tasks_timer = wx.Timer(None, -1)
    _pending_tasks_timer.Bind(wx.EVT_TIMER, _run_pending_tasks, _pending_tasks_timer)
  _pending_tasks.append( (cb, args) )

  if not _pending_tasks_timer.IsRunning():
    _pending_tasks_timer.Start(11, True)

def run_main_loop():
  _init_app()
  _app.MainLoop()

def quit_main_loop():
  _app.ExitMainLoop()

class BrowserWx(wx.Frame,BrowserBase):
  def __init__(self, baseurl):
    _init_app()
    wx.Frame.__init__(self, None, -1, "TraceViewer")
    BrowserBase.__init__(self, baseurl)
    self._webview  = wx.webkit.WebKitCtrl(self, -1)

  def load_url(self, url):
    self._webview.LoadURL("http://www.google.com")

"""Alias for BrowserWx"""
Browser = BrowserWx
