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
import browser
import message_loop
import sys
import wx
import wx.webkit

class BrowserWx(wx.Frame,browser.BrowserBase):
  def __init__(self):
    message_loop.init_main_loop()
    wx.Frame.__init__(self, None, -1, "TraceViewer",size=browser.default_size)
    browser.BrowserBase.__init__(self)

    self._webview  = wx.webkit.WebKitCtrl(self, -1)
    self._debug_ctrl = wx.TextCtrl(self, -1, "")
    self.Bind(wx.EVT_TEXT_ENTER, self.on_evt_debug_enter, self._debug_ctrl)
    self.Bind(wx.EVT_CHAR_HOOK, self.on_evt_char)

    outer_sizer = wx.BoxSizer(wx.VERTICAL)
    outer_sizer.Add(self._webview, 1, wx.ALL | wx.EXPAND)
    outer_sizer.Add(self._debug_ctrl, 0, wx.ALL | wx.EXPAND | wx.TOP, 8)

    self.SetSizer(outer_sizer)

    if browser.debug_mode:
      self._debug_ctrl.Show()
    else:
      self._debug_ctrl.Hide()
    
  def on_evt_char(self, e):
    if self.FindFocus() == self._debug_ctrl:
      if e.GetKeyCode() == 13:
        self.on_evt_debug_enter(e)
        return
    e.Skip()

  def on_evt_debug_enter(self, e):
    cmd = self._debug_ctrl.GetValue()
    self._debug_ctrl.SetValue("")
    res = self.run_javascript(cmd)
    print "> %s\n%s" % (cmd, res)

  def load_url(self, url):
    self._webview.LoadURL(url)

  def run_javascript(self, script, require_loaded = True):
    # this wraps the script in an eval, then a try-catch, and then tostrings the result in a null/undef-safe way
    # when you dont do this, it takes down WxPython completely.
    script = script.replace('"', '\\"')
    cmd = """(function() { var t = (((function() { try { return eval("%s;"); } catch(ex) { return ex; } })())); if (t === null) return 'null'; if (t === undefined) return 'undefined'; return t.toString(); })()""" % script
    return self._webview.RunScript(cmd)

  def show(self):
    self.Show()

"""Alias for BrowserWx"""
Browser = BrowserWx
