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

from browser import BrowserBase

class BrowserWx(wx.Frame,BrowserBase):
  def __init__(self):
    import message_loop_wx
    message_loop_wx._init_app()
    wx.Frame.__init__(self, None, -1, "TraceViewer")
    BrowserBase.__init__(self)
    self._webview  = wx.webkit.WebKitCtrl(self, -1)

  def load_url(self, url):
    self._webview.LoadURL(url)

  def run_javascript(self, script):
    return self._webview.RunScript(script)

  def show(self):
    self.Show()

"""Alias for BrowserWx"""
Browser = BrowserWx
