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
import gtk
import webkit

class BrowserGtk(gtk.Window,browser.BrowserBase):
  def __init__(self):
    message_loop.init_main_loop()
    gtk.Window.__init__(self)
    browser.BrowserBase.__init__(self)

    self.set_size_request(browser.default_size[0], browser.default_size[1])
    self._webview  = webkit.WebView()
    self._webview.show()

    # OK, this bit of magic is because the gtk webkit's execute_script
    # method does not actually return the script value. But, calling execute_script
    # does synchronously trigger a title-changed callback. So we make all
    # execute_script calls change the title to the result of the script,
    # then trap the title-changed callback, and return the last-seen title.
    # The title version number is a sanity check we use to ensure that the title
    # did actually change during the execute script routine, and also provides us
    # insulation in case the page itself changes the title.
    self._title = None
    self._title_version = 0
    self._webview.connect('title-changed', self.on_title_changed)

    self.add(self._webview)

  def load_url(self, url):
    self._webview.load_uri(url)

  def run_javascript(self, script):
    # this wraps the script in an eval, then a try-catch, and then tostrings the result in a null/undef-safe way
    # when you dont do this, it takes down WxPython completely.
    script = script.replace('"', '\\"')
    cmd = """document.title = (function() { var t = (((function() { try { return eval("%s;"); } catch(ex) { return ex; } })())); if (t === null) return 'null'; if (t === undefined) return 'undefined'; return t.toString(); })();""" % script
    prev_title_version = self._title_version
    self._webview.execute_script(cmd)
    assert self._title_version == prev_title_version + 1
    return self._title

  def on_title_changed(self, widget, frame, title):
    self._title = title
    self._title_version += 1

  def show(self):
    gtk.Window.show(self)

"""Alias for BrowserWx"""
Browser = BrowserGtk
