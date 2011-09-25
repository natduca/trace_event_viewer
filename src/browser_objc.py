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
import logging
import message_loop
import sys
from Foundation import *
from AppKit import *
from WebKit import *

class BrowserObjc(NSWindow,browser.BrowserBase):
  def init(self):
    message_loop.init_main_loop()
    size = NSMakeRect(0,0,800,600)
    NSWindow.initWithContentRect_styleMask_backing_defer_(
      self,
      size,
      NSTitledWindowMask | NSClosableWindowMask | NSResizableWindowMask | NSMiniaturizableWindowMask,
      NSBackingStoreBuffered,
      False)
    self.setTitle_("Hello world")
    self.contentView().setAutoresizesSubviews_(True)

    self._webview = WebView.new()
    self._webview.setFrame_(size)
    self._webview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
    self._webview.setFrameLoadDelegate_(self)
    self.contentView().addSubview_(self._webview)

    self._loaded = False
    return self
  
  def load_url(self, url):
    self._loaded = False
    print "loading", url
    self._webview.setMainFrameURL_(url)

  # frame load delegate methods
  def webView_didFinishLoadForFrame_(self, sender, frame):
    print "didfinishloading"
    if frame == self._webview.mainFrame():
      logging.debug("Load finished")
      self._loaded = True

  def run_javascript(self, script, require_loaded = True):
    if require_loaded and self._loaded == False:
      return None
    # this wraps the script in an eval, then a try-catch, and then tostrings the result in a null/undef-safe way
    # when you dont do this, it takes down WxPython completely.
    quoted_script = script.replace('"', '\\"')
    # run the script inside an eval, inside a catch, inside a function.
    cmd = """(function() { var t = (((function() { try { return eval("%s;"); } catch(ex) { return ex; } })())); if (t === null) return 'null'; if (t === undefined) return 'undefined'; return t.toString(); })();""" % quoted_script
    return self._webview.stringByEvaluatingJavaScriptFromString_(cmd)

  def show(self):
    self.makeKeyAndOrderFront_(self)
  
  def windowWillClose_(self, notification):
    print "foo"
    app.terminate_(self)

  def quit_(self, a):
    print "quit"

"""Alias for BrowserObjc"""
def Browser():
  b = BrowserObjc.new()
  return b
